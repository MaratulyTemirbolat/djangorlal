# Week 3: Mixins, Paginators, and Database Indexing

This lecture covers three important backend concepts in Django REST Framework:
reusable **Mixins**, custom **Paginators**, and **Database Indexing** via migrations.

---

## Table of Contents

1. [Mixins](#1-mixins)
   - [DRFResponseMixin](#drfresponsemixin)
   - [ModelInstanceMixin](#modelinstancemixin)
2. [Paginators](#2-paginators)
   - [Cursor Pagination](#cursor-pagination)
   - [PageNumber Pagination](#pagenumber-pagination)
   - [LimitOffset Pagination](#limitoffset-pagination)
3. [Custom Migrations](#3-custom-migrations)
   - [The Problem: Requirements Change Over Time](#the-problem-requirements-change-over-time)
   - [RunPython — Data Migration](#runpython--data-migration)
   - [RunSQL — Raw SQL in Migrations](#runsql--raw-sql-in-migrations)
4. [Database Indexing](#4-database-indexing)
   - [Composite Index](#composite-index)
   - [Partial Index](#partial-index)
   - [EXCLUDE Constraints (GiST)](#exclude-constraints-gist)

---

## 1. Mixins

Mixins are small, reusable classes that provide specific functionality. They are designed to be inherited alongside other classes (typically views) using Python's multiple inheritance. The key idea: **write once, reuse everywhere**.

### DRFResponseMixin

This mixin standardizes how DRF views build responses. Instead of repeating serialization + pagination logic in every view, you call a single method.

**What it does:**
- Accepts a queryset, serializer class, and optional paginator
- If a paginator is provided and `many=True`, it paginates the queryset first
- Otherwise, it simply serializes the data and wraps it in a `DRFResponse`

```python
class DRFResponseMixin:
    """Mixin to get DRF response."""

    def get_drf_response(
        self,
        request: DRFRequest,
        data: QuerySet | Manager,
        serializer_class: Type[Serializer],
        many: bool = False,
        paginator: Optional[BasePagination] = None,
        serializer_context: Optional[dict[str, Any]] = None,
        status_code: int = HTTP_200_OK,
    ) -> DRFResponse:
        if not serializer_context:
            serializer_context = {"request": request}
        if paginator and many:
            objects: list = paginator.paginate_queryset(
                queryset=data, request=request, view=self
            )
            serializer: Serializer = serializer_class(
                objects, many=many, context=serializer_context
            )
            return paginator.get_paginated_response(serializer.data)

        serializer: Serializer = serializer_class(
            data, many=many, context=serializer_context
        )
        return DRFResponse(data=serializer.data, status=status_code)
```

**Usage example in a view:**

```python
class UserListView(APIView, DRFResponseMixin):
    def get(self, request):
        users = CustomUser.objects.all()
        paginator = AbstractPageNumberPaginator(page_size=10)
        return self.get_drf_response(
            request=request,
            data=users,
            serializer_class=UserSerializer,
            many=True,
            paginator=paginator,
        )
```

### ModelInstanceMixin

A simple mixin that safely fetches a single model instance by arbitrary lookup fields. Returns `None` instead of raising an exception when the object is not found.

```python
class ModelInstanceMixin:
    """Mixin to get model instance."""

    def get_model_instance(
        self,
        model: Type[Model],
        **kwargs: dict[str, Any],
    ) -> Optional[Model]:
        """Get model instance or None."""
        try:
            return model.objects.get(**kwargs)
        except model.DoesNotExist:
            return None
```

**Why this is useful:** Instead of writing `try/except` blocks in every view that needs to look up an object, you call:

```python
user = self.get_model_instance(CustomUser, pk=user_id)
if user is None:
    return DRFResponse(status=404)
```

---

## 2. Paginators

Pagination splits large querysets into manageable pages. DRF provides three built-in strategies. Here we create abstract wrappers around each one with a **unified response format**.

### Cursor Pagination

Cursor pagination uses an opaque "cursor" token to navigate through results. It is the **most performant** strategy for large datasets because it does not require counting total rows.

**Key characteristics:**
- No `count` query — ideal for millions of rows
- Requires a deterministic ordering (e.g., `-created_at`)
- Clients pass a `cursor` token instead of a page number
- Cannot jump to an arbitrary page

```python
def _extract_cursor_token(
    link: Optional[str], param: str = "cursor"
) -> Optional[str]:
    """
    Returns just the cursor token from the link (?cursor=...)
    for easier frontend handling.
    """
    if not link:
        return None
    q: dict[str, Any] = parse_qs(urlparse(link).query)
    vals: list[str] = q.get(param)
    return vals[-1] if vals else None


class AbstractCursorPaginator(CursorPagination):
    DEFAULT_PAGE_SIZE = 50
    page_size_query_param = "page_size"
    cursor_query_param = "cursor"
    max_page_size = 200

    def __init__(
        self,
        page_size: int = DEFAULT_PAGE_SIZE,
        ordering: str | Sequence[str] = "-created_at",
        extra_data_return: Optional[dict[str, Any]] = None,
    ) -> None:
        self.page_size = min(page_size, AbstractCursorPaginator.max_page_size)
        self.ordering = ordering
        self.extra_data_return = extra_data_return or {}
        super().__init__()

    def get_paginated_response(self, data: ReturnList) -> DRFResponse:
        next_link: Optional[str] = self.get_next_link()
        prev_link: Optional[str] = self.get_previous_link()
        return DRFResponse(
            {
                "pagination": {
                    "next": next_link,
                    "previous": prev_link,
                    "next_cursor": _extract_cursor_token(
                        next_link, self.cursor_query_param
                    ),
                    "previous_cursor": _extract_cursor_token(
                        prev_link, self.cursor_query_param
                    ),
                    "page_size": self.get_page_size(self.request),
                    "returned": len(data),
                    "max_page_size": self.max_page_size,
                    "ordering": self.ordering,
                },
                "data": data,
                **self.extra_data_return,
            }
        )
```

**Response format:**

```json
{
  "pagination": {
    "next": "http://api.example.com/items/?cursor=cD0yMDI...",
    "previous": null,
    "next_cursor": "cD0yMDI...",
    "previous_cursor": null,
    "page_size": 50,
    "returned": 50,
    "max_page_size": 200,
    "ordering": "-created_at"
  },
  "data": [ ... ]
}
```

### PageNumber Pagination

The most intuitive pagination style. Clients request `?page=2&page_size=10`.

**Key characteristics:**
- Easy to understand for frontend developers
- Requires a `COUNT(*)` query, which can be slow on very large tables
- Supports jumping to any page

```python
class AbstractPageNumberPaginator(PageNumberPagination):
    page_size_query_param: str = "page_size"
    page_query_param: str = "page"

    def __init__(self, page_size: int = 6) -> None:
        self.page_size = page_size
        super().__init__()

    def get_paginated_response(self, data: ReturnList) -> DRFResponse:
        return DRFResponse(
            {
                "pagination": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                    "count": self.page.paginator.num_pages,
                },
                "data": data,
            }
        )
```

### LimitOffset Pagination

Similar to SQL's `LIMIT` and `OFFSET` clauses. Clients request `?limit=10&offset=20`.

**Key characteristics:**
- Familiar for developers with SQL background
- `max_limit` prevents clients from requesting too many rows at once
- Can skip rows, but suffers from the same offset performance issues as page numbers

```python
class AbstractLimitOffsetPaginator(LimitOffsetPagination):
    limit: int = 2
    limit_query_param: str = "limit"
    offset: int = 0
    offset_query_param: str = "offset"
    max_limit: int = 5

    def get_paginated_response(self, data: ReturnList) -> DRFResponse:
        return DRFResponse(
            {
                "pagination": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "data": data,
            }
        )
```

### Pagination Comparison Table

| Feature | Cursor | PageNumber | LimitOffset |
|---|---|---|---|
| Performance on large datasets | Best | Worst | Medium |
| Jump to arbitrary page | No | Yes | Yes |
| COUNT query required | No | Yes | No |
| Client complexity | Medium | Low | Low |
| Best for | Infinite scroll, feeds | Traditional pages | API consumers |

---

## 3. Custom Migrations

Django's `makemigrations` auto-generates schema changes (add column, create table, etc.), but there are situations where auto-generated migrations are not enough. That is when **custom migrations** come in — you write the migration logic yourself using `RunPython` or `RunSQL`.

### The Problem: Requirements Change Over Time

Consider a real-world scenario. Initially, each user belongs to **one** company:

```python
class CustomUser(AbstractBaseUser, PermissionsMixin, AbstractBaseModel):
    # ... other fields ...
    company = ForeignKey(
        to=Company,
        on_delete=SET_NULL,
        null=True,
        verbose_name="Company",
        help_text="Company the user belongs to",
    )
```

The system runs in production. Users have data. Then the business requirements change: **a user can now belong to multiple companies simultaneously**. So we add a `ManyToManyField`:

```python
class CustomUser(AbstractBaseUser, PermissionsMixin, AbstractBaseModel):
    # ... other fields ...

    # OLD: kept for backwards compatibility during transition
    company = ForeignKey(
        to=Company,
        on_delete=SET_NULL,
        null=True,
        verbose_name="Company",
        help_text="Company the user belongs to",
    )
    # NEW: user can belong to multiple companies
    companies = ManyToManyField(
        to=Company,
        related_name="users",
        blank=True,
        verbose_name="Companies",
        help_text="Companies the user belongs to",
    )
```

Running `makemigrations` will create the new M2M table, but it **will not** copy the existing FK data into it. Every user's `companies` set will be empty. We need a **custom data migration** to sync the old FK values into the new M2M relationship.

### RunPython — Data Migration

`RunPython` lets you execute arbitrary Python code inside a migration. This is the tool for **data transformations** — moving, copying, or converting existing data when the schema changes.

```python
from typing import Type, TYPE_CHECKING
from django.db import migrations, models
from django.db.migrations.state import StateApps
from django.db.backends.base.schema import BaseDatabaseSchemaEditor

if TYPE_CHECKING:
    from apps.auths.models import CustomUser, Company


def add_company_to_companies(
    apps: StateApps, schema_editor: BaseDatabaseSchemaEditor
) -> None:
    """Copy each user's FK company into the new M2M companies field."""
    CustomUser: Type["CustomUser"] = apps.get_model("auths", "CustomUser")
    Company: Type["Company"] = apps.get_model("auths", "Company")

    for user in CustomUser.objects.all():
        if user.company:
            user.companies.add(user.company)


def remove_company_from_companies(
    apps: StateApps, schema_editor: BaseDatabaseSchemaEditor
) -> None:
    """Reverse: clear the M2M field."""
    CustomUser: Type["CustomUser"] = apps.get_model("auths", "CustomUser")

    for user in CustomUser.objects.all():
        user.companies.clear()


class Migration(migrations.Migration):
    dependencies = [
        ('auths', '0004_customuser_companies'),
    ]

    operations = [
        migrations.RunPython(
            code=add_company_to_companies,
            # Always provide reverse_code so the migration is reversible
            reverse_code=remove_company_from_companies,
        )
    ]
```

**The migration chain looks like this:**

```
0003_company_customuser_company    ← schema: create Company model + FK on User
0004_customuser_companies          ← schema: create M2M table
0005_add_company_to_companies      ← DATA: copy FK values → M2M (RunPython)
```

**Key rules for `RunPython`:**
- **Always use `apps.get_model()`** instead of importing models directly — this gives you the model state as it was at that migration step, not the current code
- **Always provide `reverse_code`** so the migration can be rolled back with `migrate <app> <previous_number>`
- If no reverse operation makes sense, use `migrations.RunPython.noop` explicitly to signal that reversal is a no-op
- Data migrations run inside a database transaction (on supported backends like PostgreSQL)

### RunSQL — Raw SQL in Migrations

Some operations cannot be expressed through Django's ORM or Python code. For these cases, `RunSQL` lets you execute **raw SQL statements** directly. This is essential for database-specific features like extensions, constraints, and custom index types.

```python
class Migration(migrations.Migration):
    dependencies = [
        ('auths', '0005_add_company_to_companies'),
    ]

    operations = [
        # Enable the btree_gist extension (PostgreSQL-specific)
        # Required for GIST indexes on scalar types like integers
        migrations.RunSQL("CREATE EXTENSION IF NOT EXISTS btree_gist;"),

        # Create an EXCLUDE constraint to prevent overlapping subscriptions
        migrations.RunSQL(
            sql="""
                ALTER TABLE companies_subscription
                ADD CONSTRAINT prevent_overlapping_subscriptions
                EXCLUDE USING GIST (
                    company_id WITH =,
                    daterange(start_date, end_date, '[)') WITH &&
                );
            """,
            reverse_sql="""
                ALTER TABLE companies_subscription
                DROP CONSTRAINT IF EXISTS prevent_overlapping_subscriptions;
            """,
        ),
    ]
```

**Key rules for `RunSQL`:**
- **Always provide `reverse_sql`** so the migration is reversible (typically a `DROP` statement)
- Use `RunSQL` for PostgreSQL extensions, custom constraints, triggers, functions, and anything the ORM cannot express
- You can combine multiple `RunSQL` operations in the same migration

### When to Use Which

| Situation | Tool | Example |
|---|---|---|
| Transform existing data after schema change | `RunPython` | Sync FK → M2M, backfill a new column |
| Enable a PostgreSQL extension | `RunSQL` | `CREATE EXTENSION btree_gist` |
| Add a database constraint the ORM doesn't support | `RunSQL` | `EXCLUDE USING GIST (...)` |
| Create a trigger or stored procedure | `RunSQL` | `CREATE TRIGGER ...` |
| Populate a new table from existing data | `RunPython` | Copy rows from old table to new |
| Run a one-time cleanup | `RunPython` | Delete orphaned records |

---

## 4. Database Indexing

An **index** is a data structure (usually a B-tree) that the database maintains alongside your table to speed up lookups. Without an index, the DB must perform a **sequential scan** — reading every single row. With an index, it can jump directly to the matching rows.

**Trade-offs:**
- Indexes speed up `SELECT` / `WHERE` / `ORDER BY` / `JOIN` operations
- Indexes slow down `INSERT` / `UPDATE` / `DELETE` because the index must also be updated
- Indexes consume additional disk space

Django provides the `indexes` option in `Meta` to declare indexes declaratively.

### Composite Index

A **composite (multi-column) index** is an index on two or more columns. It is useful when you frequently filter or sort by a combination of fields.

**When to use:** Your queries often include `WHERE column_a = ... AND column_b = ...` together.

**Important:** Column order matters. An index on `(company_id, created_at)` can accelerate queries that filter by `company_id` alone, or by `company_id + created_at` together, but **not** by `created_at` alone (leftmost prefix rule).

```python
from django.db import models


class Subscription(models.Model):
    company = models.ForeignKey("auths.Company", on_delete=models.CASCADE)
    plan = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            # Composite index: speeds up queries like
            # Subscription.objects.filter(company=c).order_by('-created_at')
            models.Index(
                fields=["company", "-created_at"],
                name="idx_sub_company_created",
            ),
            # Another composite: speeds up lookups by company + date range
            models.Index(
                fields=["company", "start_date", "end_date"],
                name="idx_sub_company_dates",
            ),
        ]
```

**The equivalent SQL:**

```sql
CREATE INDEX idx_sub_company_created
    ON app_subscription (company_id, created_at DESC);

CREATE INDEX idx_sub_company_dates
    ON app_subscription (company_id, start_date, end_date);
```

**The leftmost prefix rule visualized:**

```
Index on (A, B, C) can accelerate:
  WHERE A = ...                   ✅
  WHERE A = ... AND B = ...       ✅
  WHERE A = ... AND B = ... AND C = ...  ✅
  WHERE B = ...                   ❌ (A is not provided)
  WHERE C = ...                   ❌
  WHERE B = ... AND C = ...       ❌
```

You can also create a composite index via a migration using raw SQL:

```python
class Migration(migrations.Migration):
    dependencies = [...]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE INDEX idx_sub_company_created
                ON auths_subscription (company_id, created_at DESC);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_sub_company_created;",
        ),
    ]
```

### Partial Index

A **partial (conditional) index** only includes rows that match a given condition. This makes the index smaller and faster than a full index, and is perfect when you only query a subset of rows.

**When to use:** You frequently filter by a condition that excludes most rows (e.g., `is_active=True`, `deleted_at IS NULL`, `status='pending'`).

```python
from django.db import models


class CustomUser(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    company = models.ForeignKey("auths.Company", on_delete=models.SET_NULL, null=True)

    class Meta:
        indexes = [
            # Partial index: only index active users
            # Speeds up: CustomUser.objects.filter(is_active=True, email=...)
            models.Index(
                fields=["email"],
                name="idx_user_email_active",
                condition=models.Q(is_active=True),
            ),
            # Partial index: only index non-deleted records
            # Speeds up: CustomUser.objects.filter(deleted_at__isnull=True)
            models.Index(
                fields=["company", "email"],
                name="idx_user_company_not_deleted",
                condition=models.Q(deleted_at__isnull=True),
            ),
        ]
```

**The equivalent SQL:**

```sql
-- Only rows where is_active = true are in the index
CREATE INDEX idx_user_email_active
    ON auths_customuser (email)
    WHERE is_active = true;

-- Only non-soft-deleted rows are indexed
CREATE INDEX idx_user_company_not_deleted
    ON auths_customuser (company_id, email)
    WHERE deleted_at IS NULL;
```

**Why partial indexes are powerful:**

```
Full index on email (1,000,000 users):
  └── Index size: ~40 MB, includes ALL rows

Partial index on email WHERE is_active = true (50,000 active users):
  └── Index size: ~2 MB, includes only active rows
  └── 20x smaller, 20x faster to scan
```

You can also combine partial + composite:

```python
models.Index(
    fields=["company", "-created_at"],
    name="idx_sub_active_company",
    condition=models.Q(is_active=True) & models.Q(deleted_at__isnull=True),
)
```

Via raw SQL migration:

```python
class Migration(migrations.Migration):
    dependencies = [...]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE INDEX idx_user_email_active
                ON auths_customuser (email)
                WHERE is_active = true;
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_user_email_active;",
        ),
    ]
```

### EXCLUDE Constraints (GiST)

This is an advanced PostgreSQL technique — using `EXCLUDE` constraints with GiST indexes to prevent overlapping date ranges (e.g., subscriptions).

```python
class Migration(migrations.Migration):
    dependencies = [
        ('auths', '0005_add_company_to_companies'),
    ]

    operations = [
        migrations.RunSQL("SELECT 1;"),  # Placeholder
        # Enable btree_gist extension for GIST index support on integer types
        # migrations.RunSQL("CREATE EXTENSION IF NOT EXISTS btree_gist;"),
        # Prevent overlapping subscriptions for the same company
        # migrations.RunSQL(
        #     sql="""
        #         ALTER TABLE companies_subscription
        #         ADD CONSTRAINT prevent_overlapping_subscriptions
        #         EXCLUDE USING GIST (
        #             company_id WITH =,
        #             daterange(start_date, end_date, '[)') WITH &&
        #         );
        #     """,
        #     reverse_sql="""
        #         ALTER TABLE companies_subscription
        #         DROP CONSTRAINT IF EXISTS prevent_overlapping_subscriptions;
        #     """,
        # ),
    ]
```

**What this does (when uncommented):**
1. `btree_gist` — a PostgreSQL extension that allows GiST indexes on scalar types (like integers)
2. `EXCLUDE USING GIST` — a constraint that prevents any two rows from having the same `company_id` AND overlapping date ranges
3. `daterange(start_date, end_date, '[)')` — creates a range that includes the start date but excludes the end date
4. `WITH &&` — the overlap operator for ranges

This is a **database-level guarantee** that no company can have two subscriptions active at the same time — much more reliable than application-level validation.

### Index Types Comparison

| Index Type | What It Does | Best For | Django API |
|---|---|---|---|
| **Single-column** | Index on one field | Simple lookups by one field | `db_index=True` on the field |
| **Composite** | Index on 2+ fields | Queries filtering/sorting by multiple fields | `Meta.indexes` with multiple `fields` |
| **Partial** | Index with a WHERE condition | Queries on a subset of rows | `Meta.indexes` with `condition=Q(...)` |
| **Unique** | Index + uniqueness constraint | Ensuring no duplicates | `unique=True` or `UniqueConstraint` |
| **GiST / EXCLUDE** | Generalized search tree | Range overlaps, geospatial data | Raw SQL via `RunSQL` |

### When to Add an Index

```
Ask yourself:
  1. Is this column used in WHERE clauses?        → Consider an index
  2. Is this column used in ORDER BY?             → Consider an index
  3. Is this column used in JOIN conditions?       → Consider an index
  4. Does the table have > 10,000 rows?           → Index becomes important
  5. Is the column highly selective (many unique values)? → Index is effective
  6. Is the column low cardinality (few unique values)?   → Index may not help
  7. Is the table write-heavy?                    → Be careful, indexes slow writes
```

Use `EXPLAIN ANALYZE` in PostgreSQL to verify that your index is actually being used:

```sql
EXPLAIN ANALYZE
SELECT * FROM auths_customuser
WHERE company_id = 5 AND is_active = true
ORDER BY created_at DESC;
```

---

## Summary

| Topic | Key Takeaway |
|---|---|
| **Mixins** | Extract common view logic into small reusable classes |
| **DRFResponseMixin** | Centralizes serialization + pagination into one method |
| **ModelInstanceMixin** | Safe object lookup that returns `None` instead of raising |
| **Cursor Pagination** | Best performance, no COUNT query, uses opaque tokens |
| **PageNumber Pagination** | Most intuitive, but requires COUNT query |
| **LimitOffset Pagination** | SQL-style, simple but can have offset performance issues |
| **RunPython** | Custom data migration — sync FK → M2M, backfill columns |
| **RunSQL** | Raw SQL in migrations — extensions, constraints, triggers |
| **Composite Index** | Multi-column index, follows leftmost prefix rule |
| **Partial Index** | Conditional index — smaller, faster, only indexes matching rows |
| **EXCLUDE / GiST** | PostgreSQL GiST indexes can enforce no-overlap rules at DB level |

This is the TypeScript and Next.js frontend for the Pilates lesson planning application.

# Architecture

The frontend is mainly implemented within `./src` and consists of the follow layers:

- `./app`
  - Contains the App Router structure with routes and pages
  - Each route is a subdirectory (e.g., `./app/exercises`)
  - Routes become publicly accessible when they have a `page.tsx` file
- `./components`
  - This package contains reusable components
  - There are two types of component
    - Components from the shadcn design system, at `./components/ui`. You are NOT allowed to edit these
    - Custom-built components, reused across pages (for example the sidebar), at `./components/custom`
  - In general, you should prefer using prebuilt shadcn components instead of custom components
- `./hooks`
  - Contains hooks that can be re-used by components, for example queries for fetching data from the API
  - Hooks and their files should be named using camelCase
- `./lib`
  - This contains lower-level library code which can be composed by hooks
  - You are NOT allowed to edit `./lib/apiClient`, which is auto-generated

# Key Patterns

## Page component structure

All pages follow this pattern:

1. Mark as `"use client"`
2. Use `PageHeader` for consistent layout
3. Call appropriate query/mutation hooks
4. Handle three states: loading (`Skeleton`), error (message), empty (CTA)
5. Use Tailwind grid for responsive layout

See `app/exercises/page.tsx:1` for complete example.

## Form handling

Forms use react-hook-form + zod validation:

1. Define Zod schema in `lib/schemas/`
2. Create mutation hook in `hooks/mutations/`
3. Use `useForm` with `zodResolver` in component
4. Wrap in shadcn `Form` component with `FormField` per input
5. Disable submit button while mutation is pending

See `app/exercises/new/page.tsx:1` for complete example.
See `lib/schemas/exercise-schema.ts:1` for Zod schema example.

## Query hooks

Query hooks abstract API calls for components:

- Name pattern: `use[Entity]` or `use[Entity]s`
- Use React Query's `useQuery` with simple string keys
- Return `{ data, isLoading, error }`
- Components never call API client directly

See `hooks/queries/useExercises.ts:1` for example.

## Mutation hooks

Mutation hooks handle creates/updates/deletes:

- Name pattern: `use[Action][Entity]`
- Use React Query's `useMutation`
- Show toast on success/error
- Invalidate relevant queries on success for automatic refetch
- Return mutation state including `isPending`

See `hooks/mutations/useCreateExercise.ts:1` for example.

### Query invalidation

Mutation hooks must invalidate related queries after success to trigger automatic refetch:

- After creating exercise → invalidate `["exercises"]`
- After generating lesson plan → invalidate `["lesson-plans"]`
- Use `queryClient.invalidateQueries({ queryKey: [...] })`

This keeps the UI in sync with backend state automatically.

## Loading, error, and empty states

All list pages must handle three states:

- Loading: Show shadcn `Skeleton` components
- Error: Display error message with error text
- Empty: Show message with CTA button to create first item

This provides consistent UX across the app.
See `app/exercises/page.tsx:35` for all three states.

## Toast notifications

Use `sonner` for user feedback in mutation hooks:

- `toast.success("Exercise created successfully")`
- `toast.error("Failed to create exercise")`
- Toaster configured in root layout

# Design

The frontend uses:

- Tailwinds CSS for custom styling
  - Prefer to use existing tailwinds classes over custom styling
- Shadcn component library
  - Prefer to use existing shadcn components over custom components

# Backend integration

## API client

The frontend integrates with the backend's API server via the API client at `./src/lib/apiClient/`.

- To update the API client inline with changes made to the backend:
  - Run the backend API server locally (run `make api` from `../backend`)
  - Generate the `apiClient` with `pnpm openapi-ts`
  - Format the `apiClient` with `pnpm format`
  - Commit the changes with message `Auto-update frontend API client using hey-api`

## Query and mutation hooks

React components may not use the API client directly. Instead, components must use a hook.

- Hooks are defined at `./src/hooks`
  - Queries must go in `./src/hooks/queries/`, and use React query's `useQuery` hook
  - Mutations must go in `./src/hooks/mutations/`, and use React query's `useMutation` hook
- Each hook should go in its own file

# Linting

After each commit, make sure the code:

- Is formatted by running `make format`
- Passes linting checks by running `make lint`

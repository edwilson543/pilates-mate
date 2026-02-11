# Architecture

The frontend is mainly implemented within `./src` and consists of the follow layers:

- `./app`
  - This is the entrypoint into the application
- `./pages`
  - This package contains the pages within the application
  - Each page should have its own component
  - Add new pages here
- `./components`
  - This package contains reusable components
  - There are two types of component
    - Components from the shadcn design system, at `./components/ui`
    - Custom-built components, reused across pages (for example the sidebar), at `./components/custom`
  - In general, you should prefer using prebuilt shadcn components instead of custom components
- `./hooks`
  - Contains hooks that can be re-used by components, for example queries for fetching data from the API
- `./lib`
  - This contains lower-level library code which can be composed by hooks

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

- Is formatted with `pnpm format`
- Passes linting checks with `pnpm lint`

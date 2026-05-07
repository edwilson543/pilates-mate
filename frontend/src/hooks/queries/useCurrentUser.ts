import { getAuthenticatedUserDetailsAuthUserGet } from "@/lib/apiClient";
import { useQuery } from "@tanstack/react-query";

export function useCurrentUser() {
  return useQuery({
    queryKey: ["current-user"],
    queryFn: async () => {
      const response = await getAuthenticatedUserDetailsAuthUserGet({
        throwOnError: true,
      });
      return response.data!;
    },
  });
}

/**
 * Shared API-related type definitions used across service clients.
 */

import type { Dayjs } from 'dayjs';

/**
 * Pagination and sorting metadata returned with paginated list responses.
 *
 * @property {number} total - Total number of items matching the query (across all pages).
 * @property {number | null} offset - Number of items skipped from the start of the result set.
 * @property {number | null} limit - Maximum number of items returned in this page.
 * @property {string} sortBy - Field name used for ordering results.
 * @property {string} sortOrder - Sort direction (`asc` or `desc`).
 * @property {FilterType[] | null} filters - Filters applied to the query, echoed back by the API.
 */
export type PaginationMetadata = {
  total: number;
  offset: number | null;
  limit: number | null;
  sortBy: string;
  sortOrder: string;
  filters: FilterType[] | null;
};

/**
 * Single column filter sent to list endpoints that support server-side filtering.
 *
 * @property {string} column - Name of the field to filter on (API column identifier).
 * @property {string} operator - Comparison operator (e.g. equals, contains) as expected by the API.
 * @property {string | number | null | Date | boolean | Dayjs} value - Right-hand value for the comparison; type depends on column and operator.
 */
export type FilterType = {
  column: string;
  operator: string;
  value: string | number | string[] | number[] | null | Date | boolean | Dayjs;
};

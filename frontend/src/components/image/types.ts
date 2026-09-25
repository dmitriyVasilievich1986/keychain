/** Props for the lazy-loaded image component with storefront icon fallback. */
export type ImageProps = {
  /** Image URL; when empty or null, the fallback icon is shown. */
  src?: string | null;
  /** Width passed to the image or icon sizing. */
  width?: number | string;
  /** Height passed to the image or icon sizing. */
  height?: number | string;
  /** Accessible label for the image or icon fallback. */
  alt?: string;
};

/** Props for the floating action button component. */
export type FloatingButtonProps = {
  /** The FAB color theme, either `primary` or `secondary`. */
  color: 'primary' | 'secondary';
  /** The content rendered inside the FAB (typically an icon). */
  children: React.ReactNode;
  /** Handler invoked when the FAB is clicked. */
  onClick: () => void;
  /** When true, disables the FAB. */
  disabled?: boolean;
};

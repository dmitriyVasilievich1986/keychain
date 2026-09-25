declare module '*.scss' {
  const classes: { readonly [key: string]: string };
  export = classes;
}

declare module '*.css' {}

declare module '*.svg' {
  const src: string;
  export default src;
}

interface ImportMetaEnv {
  readonly VITE_API_HOST?: string;
  readonly VITE_IMAGES_HOST?: string;
  readonly VITE_SOURCEMAP?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

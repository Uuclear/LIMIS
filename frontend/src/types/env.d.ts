/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<object, object, unknown>
  export default component
}

declare module 'nprogress' {
  interface NProgressOptions {
    minimum?: number
    easing?: string
    speed?: number
    trickle?: boolean
    trickleSpeed?: number
    showSpinner?: boolean
    parent?: string
    template?: string
  }

  interface NProgress {
    configure(options: NProgressOptions): NProgress
    start(): NProgress
    done(force?: boolean): NProgress
    inc(amount?: number): NProgress
    set(number: number): NProgress
    remove(): void
    isStarted(): boolean
    isRendered(): boolean
    status: number | null
  }

  const nprogress: NProgress
  export default nprogress
}

declare module 'print-js' {
  interface PrintJSOptions {
    printable: string | string[] | object[]
    type?: 'pdf' | 'html' | 'image' | 'json' | 'raw-html'
    header?: string
    headerStyle?: string
    maxWidth?: number
    properties?: Array<string | { field: string; displayName: string }>
    gridHeaderStyle?: string
    gridStyle?: string
    repeatTableHeader?: boolean
    scanStyles?: boolean
    targetStyle?: string[]
    targetStyles?: string[]
    ignoreElements?: string[]
    documentTitle?: string
    style?: string
    onLoadingStart?: () => void
    onLoadingEnd?: () => void
    onPrintDialogClose?: () => void
    onError?: (error: unknown) => void
  }

  function printJS(args: PrintJSOptions | string): void
  export default printJS
}

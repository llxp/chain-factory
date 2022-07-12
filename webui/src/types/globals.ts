export {};

declare global {
 interface Window {
   __RUNTIME_CONFIG__: {
     NODE_ENV: string;
     API_URL: string;
   };
 }
}
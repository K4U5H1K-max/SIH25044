// Test environment variable loading
console.log('=== Environment Variable Test ===');
console.log('import.meta.env.VITE_API_BASE:', import.meta.env.VITE_API_BASE);
console.log('import.meta.env.MODE:', import.meta.env.MODE);
console.log('import.meta.env.DEV:', import.meta.env.DEV);
console.log('import.meta.env.PROD:', import.meta.env.PROD);
console.log('All env vars:', import.meta.env);

// Test the API_BASE from your api.ts
import { API_BASE } from './src/utils/api.ts';
console.log('API_BASE from api.ts:', API_BASE);
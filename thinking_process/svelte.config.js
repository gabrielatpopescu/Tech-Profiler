import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	preprocess: vitePreprocess(),

	kit: {
		adapter: adapter({
			// fallback: '404.html' este important pentru Single Page Apps
			fallback: '404.html'
		}),
		paths: {
			// Dacă repository-ul tău nu este "username.github.io", 
			// ci "username.github.io/nume-repo", adaugă numele repo-ului aici:
			base: process.env.NODE_ENV === 'production' ? '/nume-repository-aici' : '',
		}
	}
};

export default config;
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
			// GitHub Pages path for TechnologyProfiler-main repository
			base: process.env.NODE_ENV === 'production' ? '/TechnologyProfiler-main' : '',
		}
	}
};

export default config;
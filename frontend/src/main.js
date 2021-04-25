import App from './App.svelte';

const app = new App({
	target: document.body,
	props: {
		pokemonVotes: {
			'bulbasaur': 0,
			'charmender': 0,
			'squirtle': 0,
		},
	}
});

export default app;
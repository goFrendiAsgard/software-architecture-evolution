<script>
	import { onMount } from 'svelte';

	export let pokemonVotes;
	let backendUrl = process.env.BACKEND_URL || 'http://localhost:3000';
	let header = process.env.HEADER || 'Pokemon Vote';
	let newPokemonName = '';
	let responseDetail = '';

	async function getVoteResult() {
		const response = await fetch(`${backendUrl}/vote`);
		return response.json();
	}

	async function vote(pokemonName) {
		const response = await fetch(`${backendUrl}/vote/${pokemonName}`, {
			method: 'POST',
			body: JSON.stringify({pokemonName}),
		});
		if (response.status == 200) {
			pokemonVotes[pokemonName] = +(pokemonVotes[pokemonName] || 0) + 1
		}
	}

	onMount(async () => {
		pokemonVotes = await getVoteResult();
		setInterval(async () => {pokemonVotes = await getVoteResult();}, 60000);
	});
</script>

<main>
	<h1>{header}</h1>
	{#each Object.entries(pokemonVotes) as [pokemonName, pokemonVote]}
		<p>{pokemonName} {pokemonVote}</p>
		<button on:click={() => vote(pokemonName)}>Vote {pokemonName}</button>
	{/each}
	<br />
	<input bind:value={newPokemonName} placeholder="New Pokemon" />
	<button on:click={() => vote(newPokemonName)}>Vote {newPokemonName}</button>
	<div>{responseDetail}</div>
</main>

<style>
	main {
		text-align: center;
		padding: 1em;
		max-width: 240px;
		margin: 0 auto;
	}

	h1 {
		color: #ff3e00;
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 100;
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
</style>
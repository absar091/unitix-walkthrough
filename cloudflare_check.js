async function main() {
  const accounts = await cloudflare.request({ method: 'GET', path: '/accounts' });
  console.log(JSON.stringify(accounts));
}
main();

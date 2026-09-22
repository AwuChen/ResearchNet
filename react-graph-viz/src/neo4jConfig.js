/**
 * Single source for Neo4j Aura settings. Keep in sync with Cred/Neo4j-398ffc2d-ResearchNet.txt
 * (instance: ResearchNet, ID: 398ffc2d)
 *
 * If you see "authentication failure": open https://console.neo4j.io → your instance →
 * reset the password, paste it here (and in Cred), rebuild/redeploy.
 *
 * CRA only embeds REACT_APP_* at build time; NEO4J_* without prefix is usually undefined in the browser.
 */

const DEFAULTS = {
  uri: 'neo4j+s://398ffc2d.databases.neo4j.io',
  user: '398ffc2d',
  password: 'pxYFawIJyzFYV_kd6IkXOc-qjNT5heD-WCGS-EgY6Jg',
  database: '398ffc2d',
};

function pickEnv(...candidates) {
  for (const v of candidates) {
    if (v == null) continue;
    const s = String(v).trim();
    if (s === '' || s === 'undefined') continue;
    return s;
  }
  return undefined;
}

export function getNeo4jConfig() {
  return {
    uri:
      pickEnv(
        process.env.REACT_APP_NEO4J_URI,
        process.env.NEO4J_URI
      ) || DEFAULTS.uri,
    user:
      pickEnv(
        process.env.REACT_APP_NEO4J_USERNAME,
        process.env.REACT_APP_NEO4J_USER,
        process.env.NEO4J_USERNAME,
        process.env.NEO4J_USER
      ) || DEFAULTS.user,
    password:
      pickEnv(
        process.env.REACT_APP_NEO4J_PASSWORD,
        process.env.NEO4J_PASSWORD
      ) || DEFAULTS.password,
    database:
      pickEnv(
        process.env.REACT_APP_NEO4J_DATABASE,
        process.env.NEO4J_DATABASE
      ) || DEFAULTS.database,
  };
}

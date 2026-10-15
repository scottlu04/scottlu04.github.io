// Static assets are served first. Future authenticated API routes can be added
// here and selected explicitly with run_worker_first in the deployment config.
export default {
  async fetch(request, env) {
    return env.ASSETS.fetch(request);
  },
};

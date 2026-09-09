window.probe = {created: [], revoked: [], active: new Set()};
const createURL = URL.createObjectURL.bind(URL);
const revokeURL = URL.revokeObjectURL.bind(URL);
URL.createObjectURL = function(value) { const url = createURL(value); probe.created.push(url); probe.active.add(url); return url; };
URL.revokeObjectURL = function(url) { probe.revoked.push(url); probe.active.delete(url); return revokeURL(url); };

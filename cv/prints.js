const cg = require("./result.json");

for (const e of cg.Nodes) {
    console.log(e.attrs.label)
}
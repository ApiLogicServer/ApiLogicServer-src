import subprocess
import sys
import logging
import shutil
from pathlib import Path



log = logging.getLogger("api_logic_server_app")
logging.basicConfig(level=logging.INFO)


ITERATE_WGAI_SCRIPT = Path(__file__).parent / "iterate_wgai_project.sh"

def iterate_project(name, id, parent_id, prompt, port):
    # ctr = 1
    # if '_' in name and name[-1].isdigit():
    #     name, ctr = name.rsplit('_', 1)
    #     ctr = int(ctr) + 1
    # name = name + f"_{ctr}"
    
    context_dir = Path('/opt/projects/by-ulid') / parent_id / 'docs'
    if not context_dir.exists():
        log.error(f"Context {context_dir} not found")
        raise FileNotFoundError(f"Context {context_dir} not found")
    
    new_prompt_id = None
    for fn in context_dir.glob('*.prompt'):
        try:
            pname, prompt_id = fn.name.rsplit('_',1)
            new_prompt_id = str(int(prompt_id.strip('.prompt')) + 1).rjust(3,'0')
        except Exception as e:
            log.error(f"Error in prompt file {fn}: {e}")
    
    if not prompt_id:
        log.error(f"No prompt file found in {context_dir}")
        raise FileNotFoundError(f"No prompt file found in {context_dir}")
    
    new_prompt_fn = context_dir / f"{pname}_{new_prompt_id}.prompt"
    log.info(f"Creating new prompt file {new_prompt_fn}")
    
    with open(new_prompt_fn, 'w') as f:
        f.write(prompt)
            
    log.info(f"Iteration - {parent_id} | {name} | {port}")
    command = ["als", "genai", "--using", str(context_dir), "--project-name", name]
    command = [str(ITERATE_WGAI_SCRIPT), name, id, str(context_dir), str(port)]
    return command


if __name__ == "__main__":
    name, id, parent_id, prompt, port = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
    command = iterate_project(name, id, parent_id, prompt, port)
    print(" ".join(command))
    #cmd_result = subprocess.Popen(command)
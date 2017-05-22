"Example files that may be used for faster initialization."
import os
import sys
import logging


logger = logging.getLogger(__name__)


def init(alias=None, template=None):
    "Initialize a templated FlowProject workflow module."
    if alias is None:
        alias = 'project'
    if template is None:
        template = 'minimal'

    if os.path.splitext(alias)[1]:
        raise RuntimeError("Please provide a name without suffix!")

    project_class_name = alias.capitalize()
    if not project_class_name.endswith('Project'):
        project_class_name += 'Project'

    for fn, code in TEMPLATES[template].items():
        try:
            fn_ = fn.format(alias=alias)   # some of the filenames may depend on the alias
            with open(fn_, 'x') as fw:
                fw.write(code.format(alias=alias, project_class=project_class_name))
        except OSError as e:
            logger.error(
                "Error while trying to initialize flow project with alias '{alias}', a file named "
                "'{fn}' already exists!".format(alias=alias, fn=fn_))
        else:
            print("Created file '{}'.".format(fn_), file=sys.stderr)


TEMPLATES = {

    'minimal': {
        '{alias}.py': """from flow import FlowProject
# import flow.environments  # uncomment to use default environments


class {project_class}(FlowProject):

    def __init__(self, *args, **kwargs):
        super({project_class}, self).__init__(*args, **kwargs)


if __name__ == '__main__':
    {project_class}().main()
""",

    },

    'example-next_operation': {
        '{alias}.py': """from flow import FlowProject
from flow import JobOperation
from flow import staticlabel
# import flow.environments  # uncomment to use default environments


class {project_class}(FlowProject):

    def __init__(self, *args, **kwargs):
        super({project_class}, self).__init__(*args, **kwargs)

    @staticlabel()
    def greeted(job):
        return job.isfile('hello.txt')

    def next_operation(self, job):
        if not self.greeted(job):
            return JobOperation(
                # The name of the operation (may be freely choosen)
                'hello',

                # A reference to the job that this operation operates on
                job,

                # The command/script to be executed for this operation
                cmd='python operations.py hello {{job}}')


if __name__ == '__main__':
    {project_class}().main()
""",

        'operations.py': """def hello(job):
    print("Hello", job)
    with job:
        with open('hello.txt', 'w') as f:
            f.write('world!')


if __name__ == '__main__':
    import flow
    flow.run()
""",
    },
    # end of example


    # example conditions:
    'example': {
        '{alias}.py': """from flow import FlowProject
from flow import staticlabel
# import flow.environments  # uncomment to use default environments


class {project_class}(FlowProject):

    @staticlabel()
    def greeted(job):
        return job.isfile('hello.txt')

    def __init__(self, *args, **kwargs):
        super({project_class}, self).__init__(*args, **kwargs)

        # Add hello world operation
        self.add_operation(

            # The name of the operation (may be freely choosen)
            name='hello',

            # The command/script to be executed for this operation; any attribute of
            # job may be used as field:
            cmd='python operations.py hello {{job._id}}',

            # Alternatively, you can construct commands/scripts dynamically by providing a callable:
            # cmd=lambda job: "python operations.py hello {{}}".format(job),

            # A list of functions that represent requirements for the execution of this operation
            # for a specific job. The requirement is met when all functions return True.
            # An empty list means: 'No requirements.'
            pre=[],

            # A list of functions that represent whether this operation is 'completed' for a
            # specific job.
            # An empty list means that the operation is never considered 'completed'.
            post=[{project_class}.greeted]

            # The number of processors required for this operation (may be a callable)
            # np = 1,
            )

if __name__ == '__main__':
    {project_class}().main()
""",

        'operations.py': """def hello(job):
    print("Hello", job)
    with job:
        with open('hello.txt', 'w') as f:
            f.write('world!')


if __name__ == '__main__':
    import flow
    flow.run()
""",
    }
}

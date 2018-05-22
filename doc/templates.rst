.. _templates:

=========
Templates
=========

The **signac-flow** package uses `jinja2`_ template scripts to generate scripts for execution and submission to cluster scheduling systems.
Templates for simple bash execution and submission to popular schedulers and compute clusters are shipped with the package.

.. _jinja2: jinja.pocoo.org


Replace the default template
============================

To customize the script generation a user can replace the default template or customize any of the provided ones.
This is an example for a basic template that would be sufficient for the simple serial execution of multiple operations:

.. code-block:: jinja

    cd {{ project.config.project_dir }}

    {% for operation in operations %}
    {{ operation.cmd }}
    {% endfor %}

To use the template above, you would store it in a file called ``templates/script.sh`` within your project root directory.

The default ``script.sh`` template only extends from the selected base template without further modification:

.. literalinclude:: ../flow/templates/script.sh
   :language: jinja


Customize provided templates
============================

Instead of simply replacing the template as shown above, we can also customize the provided templates.
One major advantage is that we can still use the template scripts for cluster submission.

Assuming that we wanted to write a time stamp to some log file before executing operations, we could provide a custom template such as this one:

.. code-block:: jinja

    {% extends base_script %}
    {% block body %}
    date >> execution.log
    {{ super() }}
    {% endblock %}

The first line indicates that this template extends an existing template called ``base_script``, which we explain in the next section.
The second and last line indicate that the enclosed lines are to be placed in the *body* block of the base template.
The third line is the actual command that we want to add and the third line ensures that the code provided by the base template within the body block is still added.


The base template
=================

The **signac-flow** package will select a different base script template depending on whether you are simply generating a script using the ``script`` command or whether you are submitting to a scheduling system with ``submit``.
In the latter case, the base script template is selected based on the available scheduling system or whether you are on any of the :ref:`officially supported environments <supported-environments>`.
This is a short illustration of that heuristic:

.. code-block:: bash

    # The `script` command always uses the same base script template:
    project.py script --> base_script='base_script.sh'

    # On system with SLURM scheduler:
    project.py submit --> base_script='slurm.sh' (extends 'base_script.sh')

    # On XSEDE Comet
    project.py submit --> base_script='comet.sh' (extends 'slurm.sh')

Regardless of which *base script template* you are actually extending from, all templates shipped with **flow** follow the same basic structure:

.. glossary::

   resources
    Calculation of the total resources required for the execution of this (submission) script.
    The base template calculates the following variables:

      ``num_tasks``:  The total number of processing units required.  [SHOULD BE NP_GLOBAL]

   header
    Directives for the scheduling system such as the cluster job name and required resources.
    This block is empty for shell script templates.

   project_header
    Commands that should be executed once before the execution of operations, such as switching into the project root directory or setting up the software environment.

   body
    All commands required for the actual execution of operations.

   footer
    Any commands that should be executed at the very end of the script.


Execution Directives
====================

Any :py:class:`~flow.FlowProject` *operation* can be amended with so called *execution directives*.
For example, to specify that we want to parallelize a particular operation on **4** processing units, we would provide the ``np=4`` directive:

.. code-block:: python

    from flow import FlowProject, directives
    from multiprocessing import Pool

    @FlowProject.operation
    @directives(np=4)
    def hello(job):
        with Pool(4) as pool:
          print("hello", job)

In general, there are no restrictions on what directives can be specified; they provide a simple way to pass additional information from an operation definition in the :py:class:`~flow.FlowProject` to the submission script.
However, **signac-flow** uses certain conventions for specific directives to provide a common language across all templates for certain common features.
For example, the ``np`` directive indicates that a particular operation requires 4 processors for execution.

The following directives are respected by all base templates shipped with **signac-flow**:

.. glossary::

    np
      The total number of processing units required for this operation.

    mpi
      The number of MPI ranks required for this operation.
      The value for *np* will default to this value unless specified separately.
      All templates will add the approriate ``mpiexec`` command to the ``prefix_cmd`` variable when this directive is specified.

    gpu
      Whether this operation requires a GPU for execution.

The combination of *np* and *mpi* allows us to realize essentially 4 execution modes:

+----------------+------------------------------+--------------------+-------------------+
| Execution Mode | Description                  | np                 | mpi               |
+================+==============================+====================+===================+
| Serial         | Simple serial execution      | 1/none             | none              |
|                | on one processor.            |                    |                   |
+----------------+------------------------------+--------------------+-------------------+
| Parallelized   | Parallelized execution       | total # processors | none              |
|                | with multiple processes      |                    |                   |
|                | or threads.                  |                    |                   |
+----------------+------------------------------+--------------------+-------------------+
| MPI            | MPI-parallelized execution   | none               | # number of ranks |
|                | with one rank per processor  |                    |                   |
+----------------+------------------------------+--------------------+-------------------+
| Hybrid MPI     | MPI-parallelized execution   | total # processors | # number of ranks |
|                | with multiple processors per |                    |                   |
|                | MPI rank                     |                    |                   |
+----------------+------------------------------+--------------------+-------------------+

For reference, this is the body block from the ``base_script.sh`` base template:

.. literalinclude:: ../flow/templates/base_script.sh
    :language: jinja
    :lines: 19-28

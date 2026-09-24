The current version of [odin](https://odinseye.info) was largerly written by Claude code with supervision. You can see this if you look through the PR and commit history pretty easily. It's a fun experiment that got a lot done quickly.

Now I want to build something by hand, with a bit more craft, that may do something very similar. I imagine it may be easier to maintain (since I will be compelled to make decisions that keep it easy to maintain by hand) and I imagine it may be more performant both because of the hands-on approach to design and implementation but also because of the lessons I learned while iterating on the original Odin.


# Pre-requisites

These are the pre-requisites for doing development in this project

- Docker
- Docker Compose
- Python 3.14
- uv (Python package manager)
- bun (JavaScript runtime, and package manager)
- make (Project management commands)
- oha (Load tests)

Perhaps eventually I will rewrite the make commands to rely exclusively on Docker, for now these tools are easy enough to install on MacOS or Linux.


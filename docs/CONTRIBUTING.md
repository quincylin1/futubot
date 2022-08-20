# Contributing

All kinds of contribution are welcome! If you would like to contribute to this project, please follow the steps below:

1. Fork and pull the latest repository of FutuBot.
2. Checkout to a new branch (please do not use the main branch for pull requests)
3. Commit your changes
4. Create a Pull Request (PR)

## Detailed Descriptions of the Contribution Steps

### Step 1: Fork and Pull the Repository

- #### Step 1.1: Click the `Fork` button on the [project page](https://github.com/quincylin1/futubot) to fork the repository from GitHub.
- #### Step 1.2: Clone the forked repository to your local computer:
  ```bash
   git clone https://github.com/<your name>/futubot.git
  ```
- #### Step 1.3: Add the official repository as upstream:
  ```shell
   git remote add upstream https://github.com/quincylin1/futubot.git
  ```

### Step 2: Add New Features to a New Branch

- #### Step 2.1: Keep your forked repository up-to-date

  Before adding new features, you need to fetch the latest branches and commits from the upstream repository and update them to your local repository:

  ```shell
   # Fetch from remote upstream
   git fetch upstream

   # Update local main branch
   git checkout main
   git rebase upstream/main

   # Update local repo
   git push origin main
  ```

- #### Step 2.2: Create a feature branch

  Before adding new features, you first need to create an issue on the official repository [github](https://github.com/quincylin1/futubot). You can then create a feature branch as follows:

  ```bash
   git checkout -b feature/issue_<index> main
   # where index is the issue index
  ```

### Step 3: Commit Your Changes

- #### Step 3.1: Run pre-commit

  Before committing new changes, please run pre-commit to solve any potential hook issues. If pre-commit is not installed on your local computer, you can install it easily using the pip command:

  ```bash
   pip install pre-commit
  ```

  Please see the [official pre-commit website](https://pre-commit.com/) for installation details.

  Once pre-commit is installed, you can then run pre-commit as follows:

  ```bash
    pre-commit run --all-files
  ```

  and resolve all the hook issues.

- #### Step 3.2: Create a Commit

  After resolving all the hook issues from pre-commit, you can then create a commit as follows:

  ```bash
  git commit -m "fix #<issue_index>: <commit_message>"
  ```

### Step 4: Create a Pull Request (PR)

- #### Step 4.1: Run pre-commit and pytest

  First run pre-commit and pytest and solve all the failures:

  ```bash
  pre-commit run --all-files
  pytest tests
  ```

- #### Step 4.2: Ensure the forked repo is up-to-date again

  ```
  git fetch upstream

  # update the main branch of your forked repo
  git checkout main
  git rebase upstream/main
  git push origin main

  # update the <new_feature_branch> branch
  git checkout <new_feature_branch>
  git rebase main
  # Solve any conflict and run pre-commit and pytest again
  ```

- #### Step 4.3: Push the \<new_feature_branch> to upstream repository

  ```
  git checkout <new_feature_branch>
  git push origin <new_feature_branch>
  ```

- #### Step 4.4: Submit a Pull Request (PR)

  Click the `pull request` button on your forked repository page on GitHub to submit a PR to the upstream main branch. Your PR will then be reviewed and accepted if there are no issues.

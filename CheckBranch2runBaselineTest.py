# this script is used to run the baseline tests
# so, whenever this script is up and run, and whenever develop branch and master branch has any change,
# this script will run all the accuracyTest, and speedPerformance Test,
# (Note: in the test implementation, the result would be written to wexfs file system,
# and invoke telemetry tool to show the result on PowerBI)


try:
    from git import Repo
    from git import Git
except ImportError:
    print("\nWarming⚠")
    print("1. Please install gitpython module. See：http://gitpython.readthedocs.io/en/stable/intro.html.")
    print("2. Or you can use the command：pip install gitpython. \n")
    exit(0)

import os
import time
import subprocess
from typing import List
import shutil

commitNameList = List[str]
# NOTE: commandLine or powershell does not work. Must be Developer  Command Prompt for VS2017
msbuild_path = r"C:\Program Files (x86)\Microsoft Visual Studio\2017\Enterprise\Common7\Tools\VsDevCmd.bat"
COMMITS_TO_PRINT = 3  # TODO change back to 3(or even 5), to ensure not missing any commit


def print_commit(commit):
    print('----')
    print(str(commit.hexsha))
    print("\"{}\" by {} ({})".format(commit.summary,
                                     commit.author.name,
                                     commit.author.email))
    print(str(commit.authored_datetime))
    print(str("count: {} and size: {}".format(commit.count(),
                                              commit.size)))


def print_repository(repo):
    print('Repo description: {}'.format(repo.description))
    print('Repo active branch is {}'.format(repo.active_branch))
    for remote in repo.remotes:
        print('Remote named "{}" with URL "{}"'.format(remote, remote.url))
    print('Last commit for repo is {}.'.format(str(repo.head.commit.hexsha)))


# please ensure that we already have the list
def readCommits(file_name: str) -> commitNameList:
    commits = []
    full_path = os.path.join(os.getcwd(), file_name + ".txt")
    with open(full_path) as file:
        for line in file:
            line = line.strip()
            commits.append(line)
    return commits


def write_commits(file_name: str, commits: str):
    full_path = os.path.join(os.getcwd(), 'Python_prototype\Monitoring', file_name + ".txt")
    with open(full_path, 'a') as file:
        file.write(commits + '\n')


def main():
    tested_master_commits = readCommits("master")
    tested_develop_commits = readCommits("develop")

    # go to the root folder of the Git repo (containing .git )
    os.chdir('..\..')
    root_dir = os.getcwd()
    repo = Repo(root_dir)
    print_repository(repo)

    assert not repo.bare, 'Could not load repository at {} :'.format(root_dir)
    repo_heads = repo.heads

    # Ensure that we have master and develop branch at local
    master_name = repo_heads['master']
    develop_name = repo_heads['develop']

    # cur_name = repo_heads['user/zhoden/addBranchMonitoringForBaselineTest']

    monitor_branches = [master_name, develop_name]

    if repo.active_branch.name != 'develop' and repo.active_branch.name != 'master':
        monitor_branches.insert(0, repo.active_branch)

    commits = list(repo.iter_commits('master'))[:COMMITS_TO_PRINT]
    for commit in commits:
        print("---------   master  branch ----------")
        print_commit(commit)

    commits = list(repo.iter_commits('develop'))[:COMMITS_TO_PRINT]
    for commit in commits:
        print("---------   develop  branch ----------")
        print_commit(commit)

    while True:
        for branch in monitor_branches:
            branch.checkout()
            subprocess.run('git pull', shell=True)
            # get latest commit ID for current branch
            p = subprocess.Popen('git rev-parse HEAD', shell=True, stdout=subprocess.PIPE)
            latest_commitID = p.communicate()[0].strip()  # compare with the lastest one in record

            if branch.name == "develop":
                if latest_commitID == tested_master_commits[-1]:
                    res = os.system(r"start /wait Python_prototype\Monitoring\buildAndRunTest.bat")
                    tested_develop_commits.append(latest_commitID)
                    write_commits('develop', latest_commitID)

            elif branch.name == 'master':
                if latest_commitID == tested_master_commits[-1]:
                    res = os.system(r"start /wait Python_prototype\Monitoring\buildAndRunTest.bat")
                    tested_develop_commits.append(latest_commitID)
                    write_commits('master', latest_commitID)

            else:  # Test the current local branch
                # raise ValueError("Are you sure want to monitor branch that is neither master nor develop?")

                valid_branch_name = branch.name.replace('/', '_')  # get a valid file name, change / into _
                res = os.system(r"start /wait Python_prototype\Monitoring\buildAndRunTest.bat")
                tested_develop_commits.append(latest_commitID)
                write_commits(valid_branch_name, latest_commitID)

            os.chdir(root_dir)
            # break  # TODO remove. add here so as not change branch

        print("Sleep for 5 seconds. Will come back later to check again.")
        time.sleep(5)  # sleep 5 seconds


    # run function will waits until the command complete and give the return code

    # if the AccuracyTest or SpeedPerformanceTest is interrupted midway. we will still remove files here.
    # shutil.rmtree('/tmp')

    # subprocess.run(), will save and display results after finishing the script, NOT incrementally
    # result = subprocess.run("buildAndRunTest.bat", cwd="Python_prototype\Monitoring", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


if __name__ == '__main__':
    main()

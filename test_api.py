import os

import pytest
import uuid

from .gitea import Gitea, User, Organization, Team, Repository, version
from .gitea import NotFoundException, AlreadyExistsException

assert version >= "0.4.0"
gitea = None

# put a ".token" file into your directory containg only the token for gitea
try:
    gitea = Gitea("http://localhost:3000", open(".token", "r").read().strip())
    print("Gitea Version: " + gitea.get_version())
    print("API-Token belongs to user: " + gitea.get_user().username)
except:
    assert (
        False
    ), "Gitea could not load. \
            - Instance running at http://localhost:3000 \
            - Token at .token   \
                ?"

#make up some fresh names for the test run
test_org = "org_" + uuid.uuid4().hex[:8]
test_user = "user_" +uuid.uuid4().hex[:8]
test_team = "team_" +uuid.uuid4().hex[:8] # team names seem to have a rather low max lenght
test_repo = "repo_" +uuid.uuid4().hex[:8]

def test_token_owner():
    assert gitea.get_user().username == "test", "Token user not 'test'."

def test_gitea_version():
    assert gitea.get_version() == "1.8.2", "Version changed. Updated?"

def test_fail_get_non_existent_user():
    with pytest.raises(NotFoundException) as e:
         User.request(gitea, test_user)

def test_fail_get_non_existent_org():
    with pytest.raises(NotFoundException) as e:
        Organization.request(gitea, test_org)

def test_fail_get_non_existent_repo():
    with pytest.raises(NotFoundException) as e:
        Repository.request(gitea, test_user, test_repo)

def test_create_user():
    email = test_user + "@example.org"
    user = gitea.create_user(test_user, email, "abcdefg123")
    user.update_mail()
    assert user.username == test_user
    assert user.login == test_user
    assert user.email == email
    assert not user.is_admin

def test_create_org():
    user = gitea.get_user()
    org = gitea.create_org(user, test_org, "some-desc", "loc")
    assert org.get_members() == [user]
    assert org.description == "some-desc"
    assert org.username == test_org
    assert org.location == "loc"
    assert not org.website
    assert not org.full_name

def test_create_repo_userowned():
    org = User.request(gitea, test_user)
    repo = gitea.create_repo(org, test_repo, "user owned repo")
    assert repo.description == "user owned repo"
    assert repo.owner == org
    assert repo.name == test_repo
    assert not repo.private

def test_create_repo_orgowned():
    org = Organization.request(gitea, test_org)
    repo = gitea.create_repo(org, test_repo, "descr")
    assert repo.description == "descr"
    assert repo.owner == org
    assert repo.name == test_repo
    assert not repo.private

def test_create_team():
    org = Organization.request(gitea, "AlreadyPresentOrg")
    team = gitea.create_team(org, test_team, "descr")
    assert team.name == test_team
    assert team.description == "descr"
    assert team.organization == org

def test_delete_repo_userowned():
    org = User.request(gitea, test_user)
    repo = Repository.request(gitea, org.username, test_repo)
    repo.delete()
    with pytest.raises(NotFoundException) as e:
        Repository.request(gitea, test_user, test_repo)

def test_delete_repo_orgowned():
    org = Organization.request(gitea, test_org)
    repo = Repository.request(gitea, org.username, test_repo)
    repo.delete()
    with pytest.raises(NotFoundException) as e:
        Repository.request(gitea, test_user, test_repo)

def test_delete_team():
    org = Organization.request(gitea, "AlreadyPresentOrg")
    team = Team.request(org, test_team)
    team.delete()
    with pytest.raises(NotFoundException) as e:
        Team.request(org, test_team)

def test_delete_org():
    org = Organization.request(gitea, test_org)
    org.delete()
    with pytest.raises(NotFoundException) as e:
        Organization.request(gitea, test_org)

def test_delete_user():
    user = User.request(gitea, test_user)
    user.delete()
    with pytest.raises(NotFoundException) as e:
        User.request(gitea, test_user)
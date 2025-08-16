import unittest
import hashlib
import time

# --- Implementations ---
# These are the actual component implementations for the CI/CD pipeline.
# The integration test will be written against these specific classes and their methods.

class VersionControlSystem:
    """A mock Version Control System."""
    def __init__(self):
        self._commits = []
        self._last_checked_commit_index = -1

    def commit(self, message, author, content, forced_hash=None):
        """Simulates a new commit."""
        timestamp = time.time()
        if forced_hash:
            commit_hash = forced_hash
        else:
            data = f"{message}{author}{content}{timestamp}".encode('utf-8')
            commit_hash = hashlib.sha1(data).hexdigest()

        commit_data = {
            'hash': commit_hash,
            'message': message,
            'author': author,
            'content': content,
            'timestamp': timestamp
        }
        self._commits.append(commit_data)
        return commit_data

    def has_new_code(self):
        """Checks if there are commits since the last check."""
        return len(self._commits) > self._last_checked_commit_index + 1

    def get_latest_commit(self):
        """Gets the most recent commit and updates the 'checked' pointer."""
        if self.has_new_code():
            self._last_checked_commit_index = len(self._commits) - 1
            return self._commits[-1]
        return None

class Builder:
    """A mock build system."""
    def __init__(self):
        self.last_built_commit = None

    def build(self, commit):
        """
        Simulates a build process.
        Returns an artifact name on success, None on failure.
        Fails if the commit message contains 'FAIL BUILD'.
        """
        if "FAIL BUILD" in commit['message']:
            return None
        self.last_built_commit = commit['hash']
        # Artifact name includes part of the commit hash for traceability
        return f"app-release-v1.0-{commit['hash'][:8]}.tar.gz"

class Tester:
    """A mock testing suite runner."""
    def __init__(self):
        self.last_tested_artifact = None

    def run_tests(self, artifact, commit):
        """
        Simulates running tests on a built artifact.
        Returns True for success, False for failure.
        Fails if the commit content contains the word 'bug'.
        """
        self.last_tested_artifact = artifact
        if 'bug' in commit['content'].lower():
            return False
        return True

class Deployer:
    """A mock deployment system."""
    def __init__(self):
        self.deployments = {}

    def deploy(self, artifact, environment):
        """
        Simulates deploying an artifact to a specific environment.
        Always returns True for this implementation.
        """
        print(f"Deploying {artifact} to {environment}")
        self.deployments[environment] = artifact
        return True

class Pipeline:
    """The CI/CD pipeline orchestrator that integrates all components."""
    def __init__(self, vcs, builder, tester, deployer, deploy_env='production'):
        self.vcs = vcs
        self.builder = builder
        self.tester = tester
        self.deployer = deployer
        self.deploy_env = deploy_env
        self.status = "Idle"
        self.last_result = None

    def run(self):
        """Runs the entire CI/CD pipeline once."""
        print("--- Pipeline run started ---")
        if not self.vcs.has_new_code():
            self.status = "No new code"
            self.last_result = ("SUCCESS", "No new commits to process.")
            print("Pipeline run finished: No new code.")
            return True

        commit = self.vcs.get_latest_commit()
        print(f"Processing commit {commit['hash'][:8]}: {commit['message']}")

        # Build step
        self.status = f"Building commit {commit['hash'][:8]}"
        artifact = self.builder.build(commit)
        if not artifact:
            self.status = "Build failed"
            self.last_result = ("FAILURE", f"Build failed for commit {commit['hash'][:8]}.")
            print("Pipeline run finished: Build failed.")
            return False
        print(f"Build successful. Artifact: {artifact}")

        # Test step
        self.status = f"Testing artifact {artifact}"
        test_passed = self.tester.run_tests(artifact, commit)
        if not test_passed:
            self.status = "Tests failed"
            self.last_result = ("FAILURE", f"Tests failed for artifact {artifact}.")
            print("Pipeline run finished: Tests failed.")
            return False
        print("Tests passed.")

        # Deploy step
        self.status = f"Deploying artifact {artifact}"
        deployed = self.deployer.deploy(artifact, self.deploy_env)
        if not deployed:
            # Our simple deployer never fails, but a real one could.
            self.status = "Deployment failed"
            self.last_result = ("FAILURE", f"Deployment failed for artifact {artifact}.")
            print("Pipeline run finished: Deployment failed.")
            return False
        
        self.status = "Deployment successful"
        self.last_result = ("SUCCESS", f"Successfully deployed {artifact} to {self.deploy_env}.")
        print(f"Pipeline run finished: Successfully deployed {artifact}.")
        return True


# --- Integration Test ---

class TestCiCdPipelineIntegration(unittest.TestCase):

    def setUp(self):
        """Set up fresh components for each test to ensure isolation."""
        self.vcs = VersionControlSystem()
        self.builder = Builder()
        self.tester = Tester()
        self.deployer = Deployer()
        self.pipeline = Pipeline(self.vcs, self.builder, self.tester, self.deployer, deploy_env='staging')

    def test_successful_full_pipeline_run(self):
        """
        Tests the entire pipeline flow from commit to successful deployment.
        This is the "happy path" integration test.
        """
        # 1. Arrange: A new, valid commit is made.
        commit = self.vcs.commit(
            message="FEAT: Add user login page",
            author="dev@example.com",
            content="<html><body>Login form</body></html>"
        )
        expected_artifact = f"app-release-v1.0-{commit['hash'][:8]}.tar.gz"

        # 2. Act: Run the pipeline.
        result = self.pipeline.run()

        # 3. Assert: Verify the outcome and the state of all components.
        self.assertTrue(result, "Pipeline should report success.")
        self.assertEqual(self.pipeline.status, "Deployment successful")

        # Verify interaction between components by checking their final state
        self.assertEqual(self.builder.last_built_commit, commit['hash'])
        self.assertEqual(self.tester.last_tested_artifact, expected_artifact)
        self.assertIn('staging', self.deployer.deployments)
        self.assertEqual(self.deployer.deployments['staging'], expected_artifact)

    def test_pipeline_stops_on_build_failure(self):
        """
        Tests that the pipeline correctly halts if the build step fails
        and does not proceed to testing or deployment.
        """
        # 1. Arrange: A commit is made that is designed to fail the build step.
        self.vcs.commit(
            message="FIX: A broken feature - FAIL BUILD",
            author="dev@example.com",
            content="This code is broken and won't compile."
        )

        # 2. Act: Run the pipeline.
        result = self.pipeline.run()

        # 3. Assert: Verify failure and that later stages were not run.
        self.assertFalse(result, "Pipeline should report failure.")
        self.assertEqual(self.pipeline.status, "Build failed")

        # Verify that tester and deployer were not called
        self.assertIsNone(self.tester.last_tested_artifact)
        self.assertNotIn('staging', self.deployer.deployments)

    def test_pipeline_stops_on_test_failure(self):
        """
        Tests that the pipeline builds successfully but halts if the test step fails,
        preventing a buggy artifact from being deployed.
        """
        # 1. Arrange: A commit is made that will build but contains a 'bug'.
        commit_with_bug = self.vcs.commit(
            message="FEAT: New calculator function",
            author="dev@example.com",
            content="function add(a, b) { return a - b; } // intentional bug"
        )
        expected_artifact = f"app-release-v1.0-{commit_with_bug['hash'][:8]}.tar.gz"

        # 2. Act: Run the pipeline.
        result = self.pipeline.run()

        # 3. Assert: Verify failure and that deployment did not happen.
        self.assertFalse(result, "Pipeline should report failure.")
        self.assertEqual(self.pipeline.status, "Tests failed")

        # Verify build happened but deployment did not
        self.assertEqual(self.builder.last_built_commit, commit_with_bug['hash'])
        self.assertEqual(self.tester.last_tested_artifact, expected_artifact)
        self.assertNotIn('staging', self.deployer.deployments)

    def test_pipeline_does_not_run_if_no_new_code(self):
        """
        Tests that the pipeline does nothing if the VCS reports no new commits.
        """
        # 1. Arrange: No commits are made.

        # 2. Act: Run the pipeline.
        result = self.pipeline.run()

        # 3. Assert: Verify it reports success (or neutral) and that no actions were taken.
        self.assertTrue(result, "Pipeline should report success for doing nothing.")
        self.assertEqual(self.pipeline.status, "No new code")
        self.assertEqual(self.pipeline.last_result[1], "No new commits to process.")

        # Verify no components were interacted with
        self.assertIsNone(self.builder.last_built_commit)
        self.assertIsNone(self.tester.last_tested_artifact)
        self.assertEqual(len(self.deployer.deployments), 0)

    def test_pipeline_runs_again_after_a_successful_run(self):
        """
        Tests that the pipeline correctly processes a second commit after a first
        successful run, demonstrating state is handled correctly between runs.
        """
        # 1. Arrange: A first successful run.
        first_commit = self.vcs.commit(
            message="Initial commit",
            author="dev@example.com",
            content="Hello World"
        )
        self.pipeline.run()
        first_artifact = f"app-release-v1.0-{first_commit['hash'][:8]}.tar.gz"

        # Verify the first run was successful
        self.assertEqual(self.deployer.deployments['staging'], first_artifact)

        # 2. Act: A second commit is made and the pipeline is run again.
        second_commit = self.vcs.commit(
            message="Update README",
            author="anotherdev@example.com",
            content="Updated documentation."
        )
        second_artifact = f"app-release-v1.0-{second_commit['hash'][:8]}.tar.gz"
        result = self.pipeline.run()

        # 3. Assert: The second run was also successful and updated the deployment.
        self.assertTrue(result)
        self.assertEqual(self.pipeline.status, "Deployment successful")
        self.assertEqual(self.builder.last_built_commit, second_commit['hash'])
        self.assertEqual(self.deployer.deployments['staging'], second_artifact)
        self.assertNotEqual(first_artifact, second_artifact)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
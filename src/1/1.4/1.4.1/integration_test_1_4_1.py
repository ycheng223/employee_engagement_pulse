import unittest
from typing import Dict, Any, List, Optional

# --- Start of Simulated Implementations ---
# In a real project, these classes would be in separate files (e.g., provider.py, resources.py, orchestrator.py)
# They are included here to make the integration test self-contained and runnable.

# --- resources.py implementation ---

class Resource:
    """Base class for all infrastructure resources."""
    def __init__(self, name: str, state: str = 'pending'):
        self.name = name
        self.id = f"res-{abs(hash(name))}"
        self.state = state

class VirtualMachine(Resource):
    """Represents a virtual machine."""
    def __init__(self, name: str, instance_type: str, image_id: str, state: str = 'pending'):
        super().__init__(name, state)
        self.instance_type = instance_type
        self.image_id = image_id

class StorageBucket(Resource):
    """Represents a cloud storage bucket."""
    def __init__(self, name: str, region: str, state: str = 'pending'):
        super().__init__(name, state)
        self.region = region

# --- provider.py implementation ---

class BaseProvider:
    """Abstract base class for cloud providers."""
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.vms: Dict[str, VirtualMachine] = {}
        self.buckets: Dict[str, StorageBucket] = {}

    def create_vm(self, name: str, instance_type: str, image_id: str) -> VirtualMachine:
        raise NotImplementedError

    def create_bucket(self, name: str, region: str) -> StorageBucket:
        raise NotImplementedError

    def destroy_vm(self, name: str) -> bool:
        raise NotImplementedError

    def destroy_bucket(self, name: str) -> bool:
        raise NotImplementedError

    def get_resource_state(self, name: str) -> Optional[str]:
        if name in self.vms:
            return self.vms[name].state
        if name in self.buckets:
            return self.buckets[name].state
        return None

class AWSProvider(BaseProvider):
    """Simulated AWS provider."""
    def __init__(self):
        super().__init__("AWS")

    def create_vm(self, name: str, instance_type: str, image_id: str) -> VirtualMachine:
        if name in self.vms:
            # Simulate idempotency
            return self.vms[name]
        print(f"AWS: Creating VM '{name}' ({instance_type})")
        vm = VirtualMachine(name, instance_type, image_id, state='running')
        self.vms[name] = vm
        return vm

    def create_bucket(self, name: str, region: str) -> StorageBucket:
        if name in self.buckets:
            return self.buckets[name]
        print(f"AWS: Creating S3 Bucket '{name}' in {region}")
        bucket = StorageBucket(name, region, state='available')
        self.buckets[name] = bucket
        return bucket

    def destroy_vm(self, name: str) -> bool:
        if name in self.vms:
            print(f"AWS: Destroying VM '{name}'")
            del self.vms[name]
            return True
        return False

    def destroy_bucket(self, name: str) -> bool:
        if name in self.buckets:
            print(f"AWS: Destroying S3 Bucket '{name}'")
            del self.buckets[name]
            return True
        return False

class GCPProvider(BaseProvider):
    """Simulated GCP provider."""
    def __init__(self):
        super().__init__("GCP")

    def create_vm(self, name: str, instance_type: str, image_id: str) -> VirtualMachine:
        if name in self.vms:
            return self.vms[name]
        print(f"GCP: Creating Compute Engine '{name}' ({instance_type})")
        vm = VirtualMachine(name, instance_type, image_id, state='RUNNING')
        self.vms[name] = vm
        return vm

    def create_bucket(self, name: str, region: str) -> StorageBucket:
        if name in self.buckets:
            return self.buckets[name]
        print(f"GCP: Creating Cloud Storage Bucket '{name}' in {region}")
        bucket = StorageBucket(name, region, state='AVAILABLE')
        self.buckets[name] = bucket
        return bucket

    def destroy_vm(self, name: str) -> bool:
        if name in self.vms:
            print(f"GCP: Destroying Compute Engine '{name}'")
            del self.vms[name]
            return True
        return False

    def destroy_bucket(self, name: str) -> bool:
        if name in self.buckets:
            print(f"GCP: Destroying Cloud Storage Bucket '{name}'")
            del self.buckets[name]
            return True
        return False

# --- orchestrator.py implementation ---

class InfrastructureOrchestrator:
    """Orchestrates the provisioning and destruction of infrastructure."""
    def __init__(self, provider: BaseProvider, config: Dict[str, Any]):
        self.provider = provider
        self.config = config
        self.managed_resources: Dict[str, Resource] = {}

    def provision(self):
        """Provisions all resources defined in the configuration."""
        print(f"--- Starting provisioning on {self.provider.provider_name} ---")
        if 'resources' not in self.config:
            return

        for res_config in self.config['resources']:
            name = res_config['name']
            res_type = res_config['type']

            if name in self.managed_resources:
                print(f"Resource '{name}' already managed. Skipping.")
                continue

            if res_type == 'vm':
                vm = self.provider.create_vm(
                    name=name,
                    instance_type=res_config['instance_type'],
                    image_id=res_config['image_id']
                )
                self.managed_resources[name] = vm
            elif res_type == 'bucket':
                bucket = self.provider.create_bucket(
                    name=name,
                    region=res_config['region']
                )
                self.managed_resources[name] = bucket
            else:
                raise ValueError(f"Unsupported resource type: {res_type}")
        print("--- Provisioning complete ---")

    def destroy(self):
        """Destroys all managed resources."""
        print(f"--- Starting destruction on {self.provider.provider_name} ---")
        names_to_destroy = list(self.managed_resources.keys())
        for name in names_to_destroy:
            resource = self.managed_resources[name]
            destroyed = False
            if isinstance(resource, VirtualMachine):
                destroyed = self.provider.destroy_vm(name)
            elif isinstance(resource, StorageBucket):
                destroyed = self.provider.destroy_bucket(name)

            if destroyed:
                del self.managed_resources[name]
            else:
                print(f"Warning: Failed to destroy '{name}', it may not exist in the provider.")
        print("--- Destruction complete ---")

    def get_status(self) -> Dict[str, str]:
        """Gets the status of all managed resources from the provider."""
        statuses = {}
        for name in self.managed_resources:
            state = self.provider.get_resource_state(name)
            statuses[name] = state if state else 'unknown'
        return statuses

# --- End of Simulated Implementations ---


# --- Start of Integration Test ---

class TestInfrastructureIntegration(unittest.TestCase):

    def setUp(self):
        """Set up a standard configuration for tests."""
        self.aws_config = {
            'provider': 'aws',
            'resources': [
                {
                    'name': 'web-server-01',
                    'type': 'vm',
                    'instance_type': 't2.micro',
                    'image_id': 'ami-0c55b159cbfafe1f0'
                },
                {
                    'name': 'app-data-bucket',
                    'type': 'bucket',
                    'region': 'us-east-1'
                }
            ]
        }
        self.gcp_config = {
            'provider': 'gcp',
            'resources': [
                {
                    'name': 'backend-instance-1',
                    'type': 'vm',
                    'instance_type': 'e2-medium',
                    'image_id': 'debian-10'
                }
            ]
        }

    def test_aws_full_lifecycle(self):
        """
        Tests the complete provision and destroy cycle using the AWS provider.
        This test verifies that the Orchestrator correctly calls the AWSProvider
        methods and that the state is consistent across both components.
        """
        # 1. Setup
        aws_provider = AWSProvider()
        orchestrator = InfrastructureOrchestrator(aws_provider, self.aws_config)

        # 2. Initial State Assertions
        self.assertEqual(len(orchestrator.managed_resources), 0)
        self.assertEqual(len(aws_provider.vms), 0)
        self.assertEqual(len(aws_provider.buckets), 0)

        # 3. Provision
        orchestrator.provision()

        # 4. Post-Provisioning Assertions (Integration Check)
        # Orchestrator should track the resources
        self.assertEqual(len(orchestrator.managed_resources), 2)
        self.assertIn('web-server-01', orchestrator.managed_resources)
        self.assertIn('app-data-bucket', orchestrator.managed_resources)

        # Provider should have "created" the resources
        self.assertEqual(len(aws_provider.vms), 1)
        self.assertEqual(len(aws_provider.buckets), 1)
        self.assertIn('web-server-01', aws_provider.vms)
        self.assertEqual(aws_provider.vms['web-server-01'].instance_type, 't2.micro')

        # Status check should reflect provider's state
        statuses = orchestrator.get_status()
        self.assertEqual(statuses['web-server-01'], 'running')
        self.assertEqual(statuses['app-data-bucket'], 'available')

        # 5. Destroy
        orchestrator.destroy()

        # 6. Post-Destruction Assertions
        # Orchestrator and Provider state should be empty
        self.assertEqual(len(orchestrator.managed_resources), 0)
        self.assertEqual(len(aws_provider.vms), 0)
        self.assertEqual(len(aws_provider.buckets), 0)

    def test_gcp_provisioning_and_status(self):
        """
        Tests provisioning with the GCP provider to ensure the orchestrator
        can integrate with different provider implementations.
        """
        # 1. Setup
        gcp_provider = GCPProvider()
        orchestrator = InfrastructureOrchestrator(gcp_provider, self.gcp_config)

        # 2. Provision
        orchestrator.provision()

        # 3. Assertions
        # Orchestrator and provider state
        self.assertEqual(len(orchestrator.managed_resources), 1)
        self.assertIn('backend-instance-1', orchestrator.managed_resources)
        self.assertEqual(len(gcp_provider.vms), 1)
        self.assertEqual(len(gcp_provider.buckets), 0) # No buckets in this config

        # Status check for GCP-specific state
        statuses = orchestrator.get_status()
        self.assertEqual(statuses['backend-instance-1'], 'RUNNING')

        # 4. Destroy
        orchestrator.destroy()
        self.assertEqual(len(gcp_provider.vms), 0)

    def test_provision_with_unsupported_resource_type(self):
        """
        Tests the integration of error handling between the orchestrator
        and the provider when an invalid resource type is specified.
        """
        bad_config = {
            'resources': [
                {'name': 'future-tech', 'type': 'quantum_computer'}
            ]
        }
        aws_provider = AWSProvider()
        orchestrator = InfrastructureOrchestrator(aws_provider, bad_config)

        # Assert that the orchestrator raises a ValueError for the unsupported type
        with self.assertRaisesRegex(ValueError, "Unsupported resource type: quantum_computer"):
            orchestrator.provision()

        # Verify that no resources were partially created
        self.assertEqual(len(aws_provider.vms), 0)
        self.assertEqual(len(aws_provider.buckets), 0)

    def test_provisioning_idempotency(self):
        """
        Tests that provisioning the same configuration twice does not create
        duplicate resources, verifying the interaction between the orchestrator's
        tracking and the provider's creation logic.
        """
        aws_provider = AWSProvider()
        orchestrator = InfrastructureOrchestrator(aws_provider, self.aws_config)

        # First provision
        orchestrator.provision()
        self.assertEqual(len(aws_provider.vms), 1)
        self.assertEqual(len(aws_provider.buckets), 1)
        # Get resource IDs to check for object stability
        vm_id_first_run = aws_provider.vms['web-server-01'].id

        # Second provision
        orchestrator.provision()

        # Assert that no new resources were created
        self.assertEqual(len(aws_provider.vms), 1, "Should not create a second VM")
        self.assertEqual(len(aws_provider.buckets), 1, "Should not create a second bucket")
        
        # Assert that the existing resource was not replaced
        vm_id_second_run = aws_provider.vms['web-server-01'].id
        self.assertEqual(vm_id_first_run, vm_id_second_run, "VM object should be the same")


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
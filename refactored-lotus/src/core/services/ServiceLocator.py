from typing import Dict, Any

class ServiceLocator:
    """
    Service Locator for managing service instances.
    This class provides centralized access to services across the application.
    
    This implementation follows the Service Locator pattern, allowing components
    to find and use services without direct dependencies.
    """
    _services: Dict[str, Any] = {}
    
    @classmethod
    def register(cls, service_name: str, service_instance: Any) -> None:
        """
        Register a service with the locator.
        
        Args:
            service_name: Name to register the service under
            service_instance: The service instance to register
        """
        cls._services[service_name] = service_instance
    
    @classmethod
    def get(cls, service_name: str) -> Any:
        """
        Get a service from the locator.
        
        Args:
            service_name: Name of the service to retrieve
            
        Returns:
            The service instance
            
        Raises:
            KeyError: If the service is not registered
        """
        if service_name not in cls._services:
            raise KeyError(f"Service '{service_name}' not registered")
        return cls._services[service_name]
    
    @classmethod
    def is_registered(cls, service_name: str) -> bool:
        """
        Check if a service is registered with the locator.
        
        Args:
            service_name: Name of the service to check
            
        Returns:
            bool: True if the service is registered, False otherwise
        """
        return service_name in cls._services
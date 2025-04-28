"""
Gerador de código Kubernetes.
"""
import os
import logging
import yaml
from typing import Dict, Any, List, Optional
import jinja2

from config import Config, logger
from models import LLMConfig

class KubernetesGenerator:
    """
    Classe para gerar código Kubernetes com base na análise de infraestrutura.
    """
    
    def __init__(self, llm_config: Optional[LLMConfig] = None):
        """
        Inicializa o gerador de código Kubernetes.
        
        Args:
            llm_config: Configuração do modelo de linguagem.
        """
        self.logger = logging.getLogger("iac_agent.kubernetes_generator")
        self.template_dir = os.path.join(Config.TEMPLATE_DIR, "kubernetes")
        self.llm_config = llm_config or LLMConfig()
        
        # Configurar ambiente Jinja2
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
    
    def generate(self, infra_analysis: Dict[str, Any], output_dir: str) -> Dict[str, str]:
        """
        Gera código Kubernetes com base na análise de infraestrutura.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            output_dir: Diretório de saída para os arquivos gerados.
            
        Returns:
            Dicionário com nomes de arquivos e conteúdos gerados.
        """
        self.logger.info("Gerando código Kubernetes")
        
        # Criar diretório de saída se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        # Inicializar dicionário de arquivos gerados
        generated_files = {}
        
        # Gerar estrutura de diretórios Kubernetes
        for env in infra_analysis.get("environments", []):
            env_dir = os.path.join(output_dir, env)
            os.makedirs(env_dir, exist_ok=True)
            
            # Gerar arquivos de namespace
            namespace_yaml = self._generate_namespace_yaml(infra_analysis, env)
            file_path = os.path.join(env, "00-namespace.yaml")
            generated_files[file_path] = namespace_yaml
            with open(os.path.join(output_dir, file_path), "w") as f:
                f.write(namespace_yaml)
            
            # Gerar arquivos de configuração
            configmap_yaml = self._generate_configmap_yaml(infra_analysis, env)
            file_path = os.path.join(env, "01-configmap.yaml")
            generated_files[file_path] = configmap_yaml
            with open(os.path.join(output_dir, file_path), "w") as f:
                f.write(configmap_yaml)
            
            secret_yaml = self._generate_secret_yaml(infra_analysis, env)
            file_path = os.path.join(env, "02-secret.yaml")
            generated_files[file_path] = secret_yaml
            with open(os.path.join(output_dir, file_path), "w") as f:
                f.write(secret_yaml)
            
            # Gerar arquivos de recursos
            resource_types = self._identify_resource_types(infra_analysis)
            for i, resource_type in enumerate(resource_types):
                resource_yaml = self._generate_resource_yaml(infra_analysis, env, resource_type)
                file_path = os.path.join(env, f"{i+3:02d}-{resource_type.lower()}.yaml")
                generated_files[file_path] = resource_yaml
                with open(os.path.join(output_dir, file_path), "w") as f:
                    f.write(resource_yaml)
            
            # Gerar arquivo kustomization.yaml
            kustomization_yaml = self._generate_kustomization_yaml(infra_analysis, env, resource_types)
            file_path = os.path.join(env, "kustomization.yaml")
            generated_files[file_path] = kustomization_yaml
            with open(os.path.join(output_dir, file_path), "w") as f:
                f.write(kustomization_yaml)
        
        # Gerar arquivo README.md
        readme_md = self._generate_readme_md(infra_analysis)
        generated_files["README.md"] = readme_md
        with open(os.path.join(output_dir, "README.md"), "w") as f:
            f.write(readme_md)
        
        return generated_files
    
    def _generate_namespace_yaml(self, infra_analysis: Dict[str, Any], environment: str) -> str:
        """
        Gera o arquivo de namespace para um ambiente específico.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            environment: Ambiente (development, staging, production).
            
        Returns:
            Conteúdo do arquivo de namespace.
        """
        # Verificar se há template disponível
        template_name = f"{environment}/namespace.yaml.j2"
        if os.path.exists(os.path.join(self.template_dir, template_name)):
            template = self.jinja_env.get_template(template_name)
            return template.render(infra=infra_analysis, environment=environment)
        
        # Gerar conteúdo básico
        namespace = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": environment,
                "labels": {
                    "name": environment,
                    "environment": environment
                }
            }
        }
        
        # Converter para YAML
        return yaml.dump(namespace, default_flow_style=False)
    
    def _generate_configmap_yaml(self, infra_analysis: Dict[str, Any], environment: str) -> str:
        """
        Gera o arquivo de ConfigMap para um ambiente específico.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            environment: Ambiente (development, staging, production).
            
        Returns:
            Conteúdo do arquivo de ConfigMap.
        """
        # Verificar se há template disponível
        template_name = f"{environment}/configmap.yaml.j2"
        if os.path.exists(os.path.join(self.template_dir, template_name)):
            template = self.jinja_env.get_template(template_name)
            return template.render(infra=infra_analysis, environment=environment)
        
        # Usar LLM para gerar o conteúdo
        prompt = f"""
        Gere um arquivo ConfigMap do Kubernetes para o ambiente {environment} com base na seguinte análise de infraestrutura:
        
        Variáveis: {infra_analysis.get("variables", {})}
        
        O arquivo deve incluir:
        1. Configurações específicas para o ambiente {environment}
        2. Valores apropriados para cada configuração
        
        Formate o código como YAML válido.
        Não inclua comentários explicativos, apenas o código Kubernetes.
        """
        
        configmap_yaml = self.llm_config.generate_text(prompt)
        if not configmap_yaml:
            # Fallback: gerar conteúdo básico
            configmap_yaml = self._generate_basic_configmap_yaml(environment)
        
        return configmap_yaml
    
    def _generate_basic_configmap_yaml(self, environment: str) -> str:
        """
        Gera um arquivo ConfigMap básico para um ambiente específico.
        
        Args:
            environment: Ambiente (development, staging, production).
            
        Returns:
            Conteúdo básico do arquivo ConfigMap.
        """
        # Configurações específicas por ambiente
        if environment == "development":
            data = {
                "ENV": "development",
                "LOG_LEVEL": "debug",
                "API_URL": "http://api-service:8000",
                "DB_HOST": "db-service",
                "DB_PORT": "5432",
                "DB_NAME": "appdb_dev",
                "CACHE_HOST": "redis-service",
                "CACHE_PORT": "6379"
            }
        elif environment == "staging":
            data = {
                "ENV": "staging",
                "LOG_LEVEL": "info",
                "API_URL": "http://api-service:8000",
                "DB_HOST": "db-service",
                "DB_PORT": "5432",
                "DB_NAME": "appdb_staging",
                "CACHE_HOST": "redis-service",
                "CACHE_PORT": "6379"
            }
        elif environment == "production":
            data = {
                "ENV": "production",
                "LOG_LEVEL": "warn",
                "API_URL": "http://api-service:8000",
                "DB_HOST": "db-service",
                "DB_PORT": "5432",
                "DB_NAME": "appdb_prod",
                "CACHE_HOST": "redis-service",
                "CACHE_PORT": "6379"
            }
        else:
            data = {
                "ENV": environment,
                "LOG_LEVEL": "info",
                "API_URL": "http://api-service:8000",
                "DB_HOST": "db-service",
                "DB_PORT": "5432",
                "DB_NAME": f"appdb_{environment}",
                "CACHE_HOST": "redis-service",
                "CACHE_PORT": "6379"
            }
        
        configmap = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "app-config",
                "namespace": environment
            },
            "data": data
        }
        
        # Converter para YAML
        return yaml.dump(configmap, default_flow_style=False)
    
    def _generate_secret_yaml(self, infra_analysis: Dict[str, Any], environment: str) -> str:
        """
        Gera o arquivo de Secret para um ambiente específico.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            environment: Ambiente (development, staging, production).
            
        Returns:
            Conteúdo do arquivo de Secret.
        """
        # Verificar se há template disponível
        template_name = f"{environment}/secret.yaml.j2"
        if os.path.exists(os.path.join(self.template_dir, template_name)):
            template = self.jinja_env.get_template(template_name)
            return template.render(infra=infra_analysis, environment=environment)
        
        # Usar LLM para gerar o conteúdo
        prompt = f"""
        Gere um arquivo Secret do Kubernetes para o ambiente {environment} com base na seguinte análise de infraestrutura:
        
        Variáveis: {infra_analysis.get("variables", {})}
        
        O arquivo deve incluir:
        1. Segredos específicos para o ambiente {environment}
        2. Valores apropriados para cada segredo (não precisa ser base64)
        
        Formate o código como YAML válido.
        Não inclua comentários explicativos, apenas o código Kubernetes.
        """
        
        secret_yaml = self.llm_config.generate_text(prompt)
        if not secret_yaml:
            # Fallback: gerar conteúdo básico
            secret_yaml = self._generate_basic_secret_yaml(environment)
        
        return secret_yaml
    
    def _generate_basic_secret_yaml(self, environment: str) -> str:
        """
        Gera um arquivo Secret básico para um ambiente específico.
        
        Args:
            environment: Ambiente (development, staging, production).
            
        Returns:
            Conteúdo básico do arquivo Secret.
        """
        # Segredos específicos por ambiente
        if environment == "development":
            string_data = {
                "DB_USER": "dev_user",
                "DB_PASSWORD": "dev_password",
                "API_KEY": "dev_api_key_12345",
                "JWT_SECRET": "dev_jwt_secret_12345"
            }
        elif environment == "staging":
            string_data = {
                "DB_USER": "staging_user",
                "DB_PASSWORD": "staging_password",
                "API_KEY": "staging_api_key_67890",
                "JWT_SECRET": "staging_jwt_secret_67890"
            }
        elif environment == "production":
            string_data = {
                "DB_USER": "prod_user",
                "DB_PASSWORD": "prod_password",
                "API_KEY": "prod_api_key_abcde",
                "JWT_SECRET": "prod_jwt_secret_abcde"
            }
        else:
            string_data = {
                "DB_USER": f"{environment}_user",
                "DB_PASSWORD": f"{environment}_password",
                "API_KEY": f"{environment}_api_key_12345",
                "JWT_SECRET": f"{environment}_jwt_secret_12345"
            }
        
        secret = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": "app-secrets",
                "namespace": environment
            },
            "type": "Opaque",
            "stringData": string_data
        }
        
        # Converter para YAML
        return yaml.dump(secret, default_flow_style=False)
    
    def _identify_resource_types(self, infra_analysis: Dict[str, Any]) -> List[str]:
        """
        Identifica tipos de recursos Kubernetes com base na análise de infraestrutura.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            
        Returns:
            Lista de tipos de recursos Kubernetes.
        """
        resource_types = []
        
        # Identificar tipos de recursos com base na análise
        for resource_type in infra_analysis.get("resources", {}).keys():
            if resource_type.startswith("v1/") or "/" in resource_type:
                parts = resource_type.split("/")
                if len(parts) >= 2:
                    kind = parts[-1]
                    if kind not in resource_types:
                        resource_types.append(kind)
        
        # Se não houver tipos de recursos identificados, adicionar tipos básicos
        if not resource_types:
            resource_types = ["Deployment", "Service", "PersistentVolumeClaim", "Ingress"]
        
        return resource_types
    
    def _generate_resource_yaml(self, infra_analysis: Dict[str, Any], environment: str, resource_type: str) -> str:
        """
        Gera o arquivo de recurso Kubernetes para um tipo específico.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            environment: Ambiente (development, staging, production).
            resource_type: Tipo de recurso Kubernetes.
            
        Returns:
            Conteúdo do arquivo de recurso.
        """
        # Verificar se há template disponível
        template_name = f"{environment}/{resource_type.lower()}.yaml.j2"
        if os.path.exists(os.path.join(self.template_dir, template_name)):
            template = self.jinja_env.get_template(template_name)
            return template.render(infra=infra_analysis, environment=environment)
        
        # Usar LLM para gerar o conteúdo
        prompt = f"""
        Gere um arquivo {resource_type} do Kubernetes para o ambiente {environment} com base na seguinte análise de infraestrutura:
        
        Recursos: {infra_analysis.get("resources", {})}
        
        O arquivo deve incluir:
        1. Configurações específicas para o recurso {resource_type} no ambiente {environment}
        2. Referências a ConfigMap e Secret quando apropriado
        3. Valores apropriados para cada configuração
        
        Formate o código como YAML válido.
        Não inclua comentários explicativos, apenas o código Kubernetes.
        """
        
        resource_yaml = self.llm_config.generate_text(prompt)
        if not resource_yaml:
            # Fallback: gerar conteúdo básico
            resource_yaml = self._generate_basic_resource_yaml(environment, resource_type)
        
        return resource_yaml
    
    def _generate_basic_resource_yaml(self, environment: str, resource_type: str) -> str:
        """
        Gera um arquivo de recurso Kubernetes básico para um tipo específico.
        
        Args:
            environment: Ambiente (development, staging, production).
            resource_type: Tipo de recurso Kubernetes.
            
        Returns:
            Conteúdo básico do arquivo de recurso.
        """
        # Configurações específicas por ambiente
        replicas = 1
        if environment == "production":
            replicas = 3
        elif environment == "staging":
            replicas = 2
        
        # Gerar recurso com base no tipo
        if resource_type == "Deployment":
            resource = {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "name": "app-deployment",
                    "namespace": environment,
                    "labels": {
                        "app": "app",
                        "environment": environment
                    }
                },
                "spec": {
                    "replicas": replicas,
                    "selector": {
                        "matchLabels": {
                            "app": "app"
                        }
                    },
                    "template": {
                        "metadata": {
                            "labels": {
                                "app": "app",
                                "environment": environment
                            }
                        },
                        "spec": {
                            "containers": [
                                {
                                    "name": "app",
                                    "image": f"app-image:{environment}",
                                    "ports": [
                                        {
                                            "containerPort": 8080
                                        }
                                    ],
                                    "envFrom": [
                                        {
                                            "configMapRef": {
                                                "name": "app-config"
                                            }
                                        },
                                        {
                                            "secretRef": {
                                                "name": "app-secrets"
                                            }
                                        }
                                    ],
                                    "resources": {
                                        "limits": {
                                            "cpu": "500m",
                                            "memory": "512Mi"
                                        },
                                        "requests": {
                                            "cpu": "100m",
                                            "memory": "128Mi"
                                        }
                                    },
                                    "livenessProbe": {
                                        "httpGet": {
                                            "path": "/health",
                                            "port": 8080
                                        },
                                        "initialDelaySeconds": 30,
                                        "periodSeconds": 10
                                    },
                                    "readinessProbe": {
                                        "httpGet": {
                                            "path": "/ready",
                                            "port": 8080
                                        },
                                        "initialDelaySeconds": 5,
                                        "periodSeconds": 5
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        elif resource_type == "Service":
            resource = {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": "app-service",
                    "namespace": environment,
                    "labels": {
                        "app": "app",
                        "environment": environment
                    }
                },
                "spec": {
                    "selector": {
                        "app": "app"
                    },
                    "ports": [
                        {
                            "port": 80,
                            "targetPort": 8080,
                            "protocol": "TCP"
                        }
                    ],
                    "type": "ClusterIP"
                }
            }
        elif resource_type == "PersistentVolumeClaim":
            resource = {
                "apiVersion": "v1",
                "kind": "PersistentVolumeClaim",
                "metadata": {
                    "name": "app-data",
                    "namespace": environment,
                    "labels": {
                        "app": "app",
                        "environment": environment
                    }
                },
                "spec": {
                    "accessModes": [
                        "ReadWriteOnce"
                    ],
                    "resources": {
                        "requests": {
                            "storage": "1Gi"
                        }
                    },
                    "storageClassName": "standard"
                }
            }
        elif resource_type == "Ingress":
            resource = {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "Ingress",
                "metadata": {
                    "name": "app-ingress",
                    "namespace": environment,
                    "labels": {
                        "app": "app",
                        "environment": environment
                    },
                    "annotations": {
                        "kubernetes.io/ingress.class": "nginx"
                    }
                },
                "spec": {
                    "rules": [
                        {
                            "host": f"app.{environment}.example.com",
                            "http": {
                                "paths": [
                                    {
                                        "path": "/",
                                        "pathType": "Prefix",
                                        "backend": {
                                            "service": {
                                                "name": "app-service",
                                                "port": {
                                                    "number": 80
                                                }
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        else:
            # Recurso genérico
            resource = {
                "apiVersion": "v1",
                "kind": resource_type,
                "metadata": {
                    "name": f"app-{resource_type.lower()}",
                    "namespace": environment,
                    "labels": {
                        "app": "app",
                        "environment": environment
                    }
                },
                "spec": {
                    "selector": {
                        "app": "app"
                    }
                }
            }
        
        # Converter para YAML
        return yaml.dump(resource, default_flow_style=False)
    
    def _generate_kustomization_yaml(self, infra_analysis: Dict[str, Any], environment: str, resource_types: List[str]) -> str:
        """
        Gera o arquivo kustomization.yaml para um ambiente específico.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            environment: Ambiente (development, staging, production).
            resource_types: Lista de tipos de recursos Kubernetes.
            
        Returns:
            Conteúdo do arquivo kustomization.yaml.
        """
        # Verificar se há template disponível
        template_name = f"{environment}/kustomization.yaml.j2"
        if os.path.exists(os.path.join(self.template_dir, template_name)):
            template = self.jinja_env.get_template(template_name)
            return template.render(infra=infra_analysis, environment=environment, resource_types=resource_types)
        
        # Gerar lista de recursos
        resources = [
            "00-namespace.yaml",
            "01-configmap.yaml",
            "02-secret.yaml"
        ]
        
        for i, resource_type in enumerate(resource_types):
            resources.append(f"{i+3:02d}-{resource_type.lower()}.yaml")
        
        # Gerar kustomization.yaml
        kustomization = {
            "apiVersion": "kustomize.config.k8s.io/v1beta1",
            "kind": "Kustomization",
            "resources": resources,
            "namespace": environment,
            "commonLabels": {
                "environment": environment,
                "managed-by": "kustomize"
            }
        }
        
        # Converter para YAML
        return yaml.dump(kustomization, default_flow_style=False)
    
    def _generate_readme_md(self, infra_analysis: Dict[str, Any]) -> str:
        """
        Gera o arquivo README.md para a infraestrutura Kubernetes.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            
        Returns:
            Conteúdo do arquivo README.md.
        """
        # Verificar se há template disponível
        if os.path.exists(os.path.join(self.template_dir, "README.md.j2")):
            template = self.jinja_env.get_template("README.md.j2")
            return template.render(infra=infra_analysis)
        
        # Gerar conteúdo básico
        environments = infra_analysis.get("environments", ["development", "staging", "production"])
        
        readme = f"""# Infraestrutura Kubernetes

Este diretório contém a infraestrutura Kubernetes para a aplicação.

## Ambientes

Os seguintes ambientes estão disponíveis:

"""
        
        for env in environments:
            readme += f"- {env}\n"
        
        readme += """
## Estrutura de Diretórios

Cada ambiente contém os seguintes arquivos:

- `00-namespace.yaml`: Namespace para o ambiente
- `01-configmap.yaml`: ConfigMap com configurações do ambiente
- `02-secret.yaml`: Secret com segredos do ambiente
- Arquivos de recursos: Deployments, Services, etc.
- `kustomization.yaml`: Configuração do Kustomize para o ambiente

## Uso

Para aplicar a configuração de um ambiente:

```bash
kubectl apply -k <ambiente>
```

Por exemplo, para aplicar o ambiente de desenvolvimento:

```bash
kubectl apply -k development
```

## Monitoramento

Para verificar o status dos recursos:

```bash
kubectl get all -n <ambiente>
```

## Logs

Para visualizar os logs da aplicação:

```bash
kubectl logs -n <ambiente> deployment/app-deployment
```
"""
        
        return readme

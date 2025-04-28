"""
Gerador de código Ansible.
"""
import os
import logging
import yaml
from typing import Dict, Any, List, Optional
import jinja2

from config import Config, logger
from models import LLMConfig

class AnsibleGenerator:
    """
    Classe para gerar código Ansible com base na análise de infraestrutura.
    """
    
    def __init__(self, llm_config: Optional[LLMConfig] = None):
        """
        Inicializa o gerador de código Ansible.
        
        Args:
            llm_config: Configuração do modelo de linguagem.
        """
        self.logger = logging.getLogger("iac_agent.ansible_generator")
        self.template_dir = os.path.join(Config.TEMPLATE_DIR, "ansible")
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
        Gera código Ansible com base na análise de infraestrutura.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            output_dir: Diretório de saída para os arquivos gerados.
            
        Returns:
            Dicionário com nomes de arquivos e conteúdos gerados.
        """
        self.logger.info("Gerando código Ansible")
        
        # Criar diretório de saída se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        # Inicializar dicionário de arquivos gerados
        generated_files = {}
        
        # Gerar estrutura de diretórios Ansible
        os.makedirs(os.path.join(output_dir, "group_vars"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "host_vars"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "roles"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "inventories"), exist_ok=True)
        
        # Gerar arquivo de configuração ansible.cfg
        ansible_cfg = self._generate_ansible_cfg(infra_analysis)
        generated_files["ansible.cfg"] = ansible_cfg
        with open(os.path.join(output_dir, "ansible.cfg"), "w") as f:
            f.write(ansible_cfg)
        
        # Gerar playbook principal
        playbook_yml = self._generate_playbook_yml(infra_analysis)
        generated_files["playbook.yml"] = playbook_yml
        with open(os.path.join(output_dir, "playbook.yml"), "w") as f:
            f.write(playbook_yml)
        
        # Gerar inventários para cada ambiente
        for env in infra_analysis.get("environments", []):
            inventory_dir = os.path.join(output_dir, "inventories", env)
            os.makedirs(inventory_dir, exist_ok=True)
            
            inventory_yml = self._generate_inventory_yml(infra_analysis, env)
            file_path = os.path.join("inventories", env, "inventory.yml")
            generated_files[file_path] = inventory_yml
            with open(os.path.join(output_dir, file_path), "w") as f:
                f.write(inventory_yml)
            
            group_vars_yml = self._generate_group_vars_yml(infra_analysis, env)
            file_path = os.path.join("group_vars", f"{env}.yml")
            generated_files[file_path] = group_vars_yml
            with open(os.path.join(output_dir, file_path), "w") as f:
                f.write(group_vars_yml)
        
        # Gerar roles com base nos recursos identificados
        roles = self._identify_roles(infra_analysis)
        for role in roles:
            role_dir = os.path.join(output_dir, "roles", role)
            os.makedirs(os.path.join(role_dir, "tasks"), exist_ok=True)
            os.makedirs(os.path.join(role_dir, "handlers"), exist_ok=True)
            os.makedirs(os.path.join(role_dir, "templates"), exist_ok=True)
            os.makedirs(os.path.join(role_dir, "defaults"), exist_ok=True)
            os.makedirs(os.path.join(role_dir, "vars"), exist_ok=True)
            
            # Gerar arquivos da role
            main_yml = self._generate_role_main_yml(infra_analysis, role)
            file_path = os.path.join("roles", role, "tasks", "main.yml")
            generated_files[file_path] = main_yml
            with open(os.path.join(output_dir, file_path), "w") as f:
                f.write(main_yml)
            
            handlers_yml = self._generate_role_handlers_yml(infra_analysis, role)
            file_path = os.path.join("roles", role, "handlers", "main.yml")
            generated_files[file_path] = handlers_yml
            with open(os.path.join(output_dir, file_path), "w") as f:
                f.write(handlers_yml)
            
            defaults_yml = self._generate_role_defaults_yml(infra_analysis, role)
            file_path = os.path.join("roles", role, "defaults", "main.yml")
            generated_files[file_path] = defaults_yml
            with open(os.path.join(output_dir, file_path), "w") as f:
                f.write(defaults_yml)
        
        return generated_files
    
    def _generate_ansible_cfg(self, infra_analysis: Dict[str, Any]) -> str:
        """
        Gera o arquivo ansible.cfg.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            
        Returns:
            Conteúdo do arquivo ansible.cfg.
        """
        # Verificar se há template disponível
        if os.path.exists(os.path.join(self.template_dir, "ansible.cfg.j2")):
            template = self.jinja_env.get_template("ansible.cfg.j2")
            return template.render(infra=infra_analysis)
        
        # Gerar conteúdo básico
        return """[defaults]
inventory = ./inventories/development/inventory.yml
roles_path = ./roles
host_key_checking = False
retry_files_enabled = False
stdout_callback = yaml
bin_ansible_callbacks = True

[privilege_escalation]
become = True
become_method = sudo
become_user = root
become_ask_pass = False

[ssh_connection]
pipelining = True
control_path = /tmp/ansible-ssh-%%h-%%p-%%r
"""
    
    def _generate_playbook_yml(self, infra_analysis: Dict[str, Any]) -> str:
        """
        Gera o arquivo playbook.yml.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            
        Returns:
            Conteúdo do arquivo playbook.yml.
        """
        # Verificar se há template disponível
        if os.path.exists(os.path.join(self.template_dir, "playbook.yml.j2")):
            template = self.jinja_env.get_template("playbook.yml.j2")
            return template.render(infra=infra_analysis)
        
        # Gerar com base na análise
        roles = self._identify_roles(infra_analysis)
        
        # Usar LLM para gerar o conteúdo
        prompt = f"""
        Gere um arquivo playbook.yml do Ansible com base na seguinte análise de infraestrutura:
        
        Recursos: {infra_analysis.get("resources", {})}
        Roles identificadas: {roles}
        
        O arquivo deve incluir:
        1. Hosts a serem gerenciados
        2. Variáveis globais
        3. Roles a serem aplicadas
        4. Tarefas específicas, se necessário
        
        Formate o código como YAML válido.
        Não inclua comentários explicativos, apenas o código Ansible.
        """
        
        playbook_yml = self.llm_config.generate_text(prompt)
        if not playbook_yml:
            # Fallback: gerar conteúdo básico
            playbook_yml = self._generate_basic_playbook_yml(infra_analysis, roles)
        
        return playbook_yml
    
    def _generate_basic_playbook_yml(self, infra_analysis: Dict[str, Any], roles: List[str]) -> str:
        """
        Gera um arquivo playbook.yml básico.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            roles: Lista de roles identificadas.
            
        Returns:
            Conteúdo básico do arquivo playbook.yml.
        """
        playbook = []
        
        # Adicionar play para cada ambiente
        for env in infra_analysis.get("environments", ["development"]):
            play = {
                "name": f"Configure {env} environment",
                "hosts": env,
                "become": True,
                "vars": {
                    "environment": env
                },
                "roles": []
            }
            
            # Adicionar roles
            for role in roles:
                play["roles"].append(role)
            
            playbook.append(play)
        
        # Converter para YAML
        return yaml.dump(playbook, default_flow_style=False)
    
    def _generate_inventory_yml(self, infra_analysis: Dict[str, Any], environment: str) -> str:
        """
        Gera o arquivo inventory.yml para um ambiente específico.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            environment: Ambiente (development, staging, production).
            
        Returns:
            Conteúdo do arquivo inventory.yml.
        """
        # Verificar se há template disponível
        template_name = f"inventory/{environment}.yml.j2"
        if os.path.exists(os.path.join(self.template_dir, template_name)):
            template = self.jinja_env.get_template(template_name)
            return template.render(infra=infra_analysis, environment=environment)
        
        # Gerar com base na análise
        hosts = []
        for resource_type, resources in infra_analysis.get("resources", {}).items():
            if resource_type == "ansible_host":
                hosts.extend(resources)
        
        # Usar LLM para gerar o conteúdo
        prompt = f"""
        Gere um arquivo inventory.yml do Ansible para o ambiente {environment} com base na seguinte análise de infraestrutura:
        
        Hosts: {hosts}
        
        O arquivo deve incluir:
        1. Grupos de hosts para o ambiente {environment}
        2. Variáveis de host, como ansible_host, ansible_user, etc.
        3. Grupos aninhados, se apropriado
        
        Formate o código como YAML válido.
        Não inclua comentários explicativos, apenas o código Ansible.
        """
        
        inventory_yml = self.llm_config.generate_text(prompt)
        if not inventory_yml:
            # Fallback: gerar conteúdo básico
            inventory_yml = self._generate_basic_inventory_yml(environment)
        
        return inventory_yml
    
    def _generate_basic_inventory_yml(self, environment: str) -> str:
        """
        Gera um arquivo inventory.yml básico para um ambiente específico.
        
        Args:
            environment: Ambiente (development, staging, production).
            
        Returns:
            Conteúdo básico do arquivo inventory.yml.
        """
        inventory = {
            "all": {
                "children": {
                    environment: {
                        "children": {
                            "web": {
                                "hosts": {
                                    f"web1.{environment}.example.com": {
                                        "ansible_host": "192.168.1.10",
                                        "ansible_user": "ubuntu"
                                    },
                                    f"web2.{environment}.example.com": {
                                        "ansible_host": "192.168.1.11",
                                        "ansible_user": "ubuntu"
                                    }
                                }
                            },
                            "db": {
                                "hosts": {
                                    f"db1.{environment}.example.com": {
                                        "ansible_host": "192.168.1.20",
                                        "ansible_user": "ubuntu"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        # Converter para YAML
        return yaml.dump(inventory, default_flow_style=False)
    
    def _generate_group_vars_yml(self, infra_analysis: Dict[str, Any], environment: str) -> str:
        """
        Gera o arquivo group_vars/environment.yml para um ambiente específico.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            environment: Ambiente (development, staging, production).
            
        Returns:
            Conteúdo do arquivo group_vars/environment.yml.
        """
        # Verificar se há template disponível
        template_name = f"group_vars/{environment}.yml.j2"
        if os.path.exists(os.path.join(self.template_dir, template_name)):
            template = self.jinja_env.get_template(template_name)
            return template.render(infra=infra_analysis, environment=environment)
        
        # Gerar com base na análise
        variables = infra_analysis.get("variables", {})
        
        # Usar LLM para gerar o conteúdo
        prompt = f"""
        Gere um arquivo group_vars/{environment}.yml do Ansible com base na seguinte análise de infraestrutura:
        
        Variáveis: {variables}
        
        O arquivo deve incluir:
        1. Variáveis específicas para o ambiente {environment}
        2. Valores apropriados para cada variável
        
        Formate o código como YAML válido.
        Não inclua comentários explicativos, apenas o código Ansible.
        """
        
        group_vars_yml = self.llm_config.generate_text(prompt)
        if not group_vars_yml:
            # Fallback: gerar conteúdo básico
            group_vars_yml = self._generate_basic_group_vars_yml(environment)
        
        return group_vars_yml
    
    def _generate_basic_group_vars_yml(self, environment: str) -> str:
        """
        Gera um arquivo group_vars/environment.yml básico para um ambiente específico.
        
        Args:
            environment: Ambiente (development, staging, production).
            
        Returns:
            Conteúdo básico do arquivo group_vars/environment.yml.
        """
        # Configurações específicas por ambiente
        if environment == "development":
            vars_dict = {
                "env": "development",
                "debug_mode": True,
                "app_port": 8000,
                "db_host": "db1.development.example.com",
                "db_name": "appdb_dev",
                "db_user": "devuser",
                "db_password": "devpassword"
            }
        elif environment == "staging":
            vars_dict = {
                "env": "staging",
                "debug_mode": False,
                "app_port": 8000,
                "db_host": "db1.staging.example.com",
                "db_name": "appdb_staging",
                "db_user": "staginguser",
                "db_password": "stagingpassword"
            }
        elif environment == "production":
            vars_dict = {
                "env": "production",
                "debug_mode": False,
                "app_port": 80,
                "db_host": "db1.production.example.com",
                "db_name": "appdb_prod",
                "db_user": "produser",
                "db_password": "prodpassword"
            }
        else:
            vars_dict = {
                "env": environment,
                "debug_mode": False,
                "app_port": 8000,
                "db_host": f"db1.{environment}.example.com",
                "db_name": f"appdb_{environment}",
                "db_user": f"{environment}user",
                "db_password": f"{environment}password"
            }
        
        # Converter para YAML
        return yaml.dump(vars_dict, default_flow_style=False)
    
    def _identify_roles(self, infra_analysis: Dict[str, Any]) -> List[str]:
        """
        Identifica roles com base na análise de infraestrutura.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            
        Returns:
            Lista de roles identificadas.
        """
        roles = set()
        
        # Identificar roles com base nos recursos
        for resource_type, resources in infra_analysis.get("resources", {}).items():
            if resource_type == "apt" or resource_type == "yum" or resource_type == "package":
                roles.add("common")
            elif resource_type == "service":
                roles.add("services")
            elif resource_type == "user" or resource_type == "group":
                roles.add("users")
            elif resource_type == "file" or resource_type == "template" or resource_type == "copy":
                roles.add("files")
            elif resource_type == "mysql_db" or resource_type == "postgresql_db":
                roles.add("database")
            elif resource_type == "docker_container" or resource_type == "docker_image":
                roles.add("docker")
            elif resource_type == "git":
                roles.add("deploy")
            elif resource_type == "firewalld" or resource_type == "ufw":
                roles.add("firewall")
            elif resource_type == "cron":
                roles.add("cron")
            elif resource_type == "mount" or resource_type == "filesystem":
                roles.add("storage")
        
        # Se não houver roles identificadas, adicionar roles básicas
        if not roles:
            roles = {"common", "webserver", "database"}
        
        return sorted(list(roles))
    
    def _generate_role_main_yml(self, infra_analysis: Dict[str, Any], role: str) -> str:
        """
        Gera o arquivo main.yml para uma role específica.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            role: Nome da role.
            
        Returns:
            Conteúdo do arquivo main.yml da role.
        """
        # Verificar se há template disponível
        template_name = f"roles/{role}/tasks/main.yml.j2"
        if os.path.exists(os.path.join(self.template_dir, template_name)):
            template = self.jinja_env.get_template(template_name)
            return template.render(infra=infra_analysis, role=role)
        
        # Usar LLM para gerar o conteúdo
        prompt = f"""
        Gere um arquivo main.yml de tarefas do Ansible para a role '{role}' com base na seguinte análise de infraestrutura:
        
        Recursos: {infra_analysis.get("resources", {})}
        
        O arquivo deve incluir:
        1. Tarefas específicas para a role '{role}'
        2. Uso de módulos Ansible apropriados
        3. Handlers quando necessário
        4. Variáveis da role
        
        Formate o código como YAML válido.
        Não inclua comentários explicativos, apenas o código Ansible.
        """
        
        main_yml = self.llm_config.generate_text(prompt)
        if not main_yml:
            # Fallback: gerar conteúdo básico
            main_yml = self._generate_basic_role_main_yml(role)
        
        return main_yml
    
    def _generate_basic_role_main_yml(self, role: str) -> str:
        """
        Gera um arquivo main.yml básico para uma role específica.
        
        Args:
            role: Nome da role.
            
        Returns:
            Conteúdo básico do arquivo main.yml da role.
        """
        tasks = []
        
        # Tarefas específicas por role
        if role == "common":
            tasks = [
                {
                    "name": "Update apt cache",
                    "apt": {
                        "update_cache": True,
                        "cache_valid_time": 3600
                    }
                },
                {
                    "name": "Install common packages",
                    "apt": {
                        "name": ["vim", "curl", "git", "htop", "net-tools"],
                        "state": "present"
                    }
                },
                {
                    "name": "Configure timezone",
                    "timezone": {
                        "name": "{{ timezone | default('UTC') }}"
                    }
                }
            ]
        elif role == "webserver":
            tasks = [
                {
                    "name": "Install web server packages",
                    "apt": {
                        "name": ["nginx", "python3-pip"],
                        "state": "present"
                    }
                },
                {
                    "name": "Ensure nginx is running and enabled",
                    "service": {
                        "name": "nginx",
                        "state": "started",
                        "enabled": True
                    }
                },
                {
                    "name": "Copy nginx configuration",
                    "template": {
                        "src": "nginx.conf.j2",
                        "dest": "/etc/nginx/sites-available/default",
                        "owner": "root",
                        "group": "root",
                        "mode": "0644"
                    },
                    "notify": "Restart nginx"
                }
            ]
        elif role == "database":
            tasks = [
                {
                    "name": "Install database packages",
                    "apt": {
                        "name": ["mysql-server", "python3-pymysql"],
                        "state": "present"
                    }
                },
                {
                    "name": "Ensure MySQL is running and enabled",
                    "service": {
                        "name": "mysql",
                        "state": "started",
                        "enabled": True
                    }
                },
                {
                    "name": "Create MySQL database",
                    "mysql_db": {
                        "name": "{{ db_name }}",
                        "state": "present"
                    }
                },
                {
                    "name": "Create MySQL user",
                    "mysql_user": {
                        "name": "{{ db_user }}",
                        "password": "{{ db_password }}",
                        "priv": "{{ db_name }}.*:ALL",
                        "host": "localhost",
                        "state": "present"
                    }
                }
            ]
        elif role == "docker":
            tasks = [
                {
                    "name": "Install required packages",
                    "apt": {
                        "name": ["apt-transport-https", "ca-certificates", "curl", "gnupg", "lsb-release"],
                        "state": "present"
                    }
                },
                {
                    "name": "Add Docker GPG key",
                    "apt_key": {
                        "url": "https://download.docker.com/linux/ubuntu/gpg",
                        "state": "present"
                    }
                },
                {
                    "name": "Add Docker repository",
                    "apt_repository": {
                        "repo": "deb [arch=amd64] https://download.docker.com/linux/ubuntu {{ ansible_distribution_release }} stable",
                        "state": "present"
                    }
                },
                {
                    "name": "Install Docker",
                    "apt": {
                        "name": ["docker-ce", "docker-ce-cli", "containerd.io"],
                        "state": "present",
                        "update_cache": True
                    }
                },
                {
                    "name": "Ensure Docker is running and enabled",
                    "service": {
                        "name": "docker",
                        "state": "started",
                        "enabled": True
                    }
                }
            ]
        elif role == "users":
            tasks = [
                {
                    "name": "Create application group",
                    "group": {
                        "name": "{{ app_group | default('app') }}",
                        "state": "present"
                    }
                },
                {
                    "name": "Create application user",
                    "user": {
                        "name": "{{ app_user | default('app') }}",
                        "group": "{{ app_group | default('app') }}",
                        "shell": "/bin/bash",
                        "state": "present"
                    }
                },
                {
                    "name": "Set up authorized keys for application user",
                    "authorized_key": {
                        "user": "{{ app_user | default('app') }}",
                        "key": "{{ lookup('file', 'files/id_rsa.pub') }}"
                    },
                    "when": "app_user_key is defined"
                }
            ]
        else:
            tasks = [
                {
                    "name": f"Example task for role {role}",
                    "debug": {
                        "msg": f"This is a placeholder task for role {role}"
                    }
                }
            ]
        
        # Converter para YAML
        return yaml.dump(tasks, default_flow_style=False)
    
    def _generate_role_handlers_yml(self, infra_analysis: Dict[str, Any], role: str) -> str:
        """
        Gera o arquivo handlers/main.yml para uma role específica.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            role: Nome da role.
            
        Returns:
            Conteúdo do arquivo handlers/main.yml da role.
        """
        # Verificar se há template disponível
        template_name = f"roles/{role}/handlers/main.yml.j2"
        if os.path.exists(os.path.join(self.template_dir, template_name)):
            template = self.jinja_env.get_template(template_name)
            return template.render(infra=infra_analysis, role=role)
        
        # Gerar handlers básicos
        handlers = []
        
        # Handlers específicos por role
        if role == "webserver":
            handlers = [
                {
                    "name": "Restart nginx",
                    "service": {
                        "name": "nginx",
                        "state": "restarted"
                    }
                }
            ]
        elif role == "database":
            handlers = [
                {
                    "name": "Restart MySQL",
                    "service": {
                        "name": "mysql",
                        "state": "restarted"
                    }
                }
            ]
        elif role == "docker":
            handlers = [
                {
                    "name": "Restart Docker",
                    "service": {
                        "name": "docker",
                        "state": "restarted"
                    }
                }
            ]
        
        # Converter para YAML
        return yaml.dump(handlers, default_flow_style=False)
    
    def _generate_role_defaults_yml(self, infra_analysis: Dict[str, Any], role: str) -> str:
        """
        Gera o arquivo defaults/main.yml para uma role específica.
        
        Args:
            infra_analysis: Resultado da análise de infraestrutura.
            role: Nome da role.
            
        Returns:
            Conteúdo do arquivo defaults/main.yml da role.
        """
        # Verificar se há template disponível
        template_name = f"roles/{role}/defaults/main.yml.j2"
        if os.path.exists(os.path.join(self.template_dir, template_name)):
            template = self.jinja_env.get_template(template_name)
            return template.render(infra=infra_analysis, role=role)
        
        # Gerar defaults básicos
        defaults = {}
        
        # Defaults específicos por role
        if role == "common":
            defaults = {
                "timezone": "UTC",
                "ntp_servers": ["0.pool.ntp.org", "1.pool.ntp.org"]
            }
        elif role == "webserver":
            defaults = {
                "http_port": 80,
                "https_port": 443,
                "app_root": "/var/www/app"
            }
        elif role == "database":
            defaults = {
                "db_name": "appdb",
                "db_user": "appuser",
                "db_password": "apppassword",
                "db_host": "localhost"
            }
        elif role == "docker":
            defaults = {
                "docker_users": ["ubuntu"],
                "docker_compose_version": "1.29.2"
            }
        elif role == "users":
            defaults = {
                "app_user": "app",
                "app_group": "app",
                "app_user_key": None
            }
        
        # Converter para YAML
        return yaml.dump(defaults, default_flow_style=False)

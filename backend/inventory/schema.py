"""
Schéma GraphQL pour l'API d'inventaire
"""

import graphene
from graphene_django import DjangoObjectType
from django.utils import timezone
from .models import Computer, Software, InventoryLog


class ComputerType(DjangoObjectType):
    """Type GraphQL pour les ordinateurs"""
    
    class Meta:
        model = Computer
        fields = '__all__'


class SoftwareType(DjangoObjectType):
    """Type GraphQL pour les logiciels"""
    
    class Meta:
        model = Software
        fields = '__all__'


class InventoryLogType(DjangoObjectType):
    """Type GraphQL pour les logs d'inventaire"""
    
    class Meta:
        model = InventoryLog
        fields = '__all__'


class ComputerInput(graphene.InputObjectType):
    """Input GraphQL pour les ordinateurs"""
    hostname = graphene.String(required=True)
    serialNumber = graphene.String(required=True)
    manufacturer = graphene.String()
    model = graphene.String()
    currentUser = graphene.String()
    systemInfo = graphene.JSONString()
    hardwareInfo = graphene.JSONString()
    networkInfo = graphene.JSONString()


class SoftwareInput(graphene.InputObjectType):
    """Input GraphQL pour les logiciels"""
    computerId = graphene.Int(required=True)
    name = graphene.String(required=True)
    version = graphene.String()
    publisher = graphene.String()
    installDate = graphene.String()
    detectionDate = graphene.DateTime()


class CreateComputerMutation(graphene.Mutation):
    """Mutation pour créer un ordinateur"""
    
    class Arguments:
        input = ComputerInput(required=True)
    
    computer = graphene.Field(ComputerType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, input):
        try:
            # Créer l'ordinateur
            computer = Computer.objects.create(
                hostname=input.hostname,
                serial_number=input.serialNumber,
                manufacturer=input.manufacturer or "Unknown",
                model=input.model or "Unknown",
                current_user=input.currentUser or "Unknown",
                system_info=input.systemInfo or {},
                hardware_info=input.hardwareInfo or {},
                network_info=input.networkInfo or {}
            )
            
            # Créer un log
            InventoryLog.log_scan(
                computer=computer,
                message="Ordinateur créé via GraphQL",
                details={'source': 'graphql'}
            )
            
            return CreateComputerMutation(
                computer=computer,
                success=True,
                errors=[]
            )
            
        except Exception as e:
            return CreateComputerMutation(
                computer=None,
                success=False,
                errors=[str(e)]
            )


class UpdateComputerMutation(graphene.Mutation):
    """Mutation pour mettre à jour un ordinateur"""
    
    class Arguments:
        id = graphene.ID(required=True)
        input = ComputerInput(required=True)
    
    computer = graphene.Field(ComputerType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, id, input):
        try:
            # Récupérer l'ordinateur
            computer = Computer.objects.get(id=id)
            
            # Mettre à jour l'ordinateur
            computer.hostname = input.hostname
            computer.serial_number = input.serialNumber
            computer.manufacturer = input.manufacturer or computer.manufacturer
            computer.model = input.model or computer.model
            computer.current_user = input.currentUser or computer.current_user
            
            if input.systemInfo:
                computer.system_info = input.systemInfo
            if input.hardwareInfo:
                computer.hardware_info = input.hardwareInfo
            if input.networkInfo:
                computer.network_info = input.networkInfo
            
            computer.update_last_seen()
            computer.save()
            
            # Créer un log
            InventoryLog.log_scan(
                computer=computer,
                message="Ordinateur mis à jour via GraphQL",
                details={'source': 'graphql'}
            )
            
            return UpdateComputerMutation(
                computer=computer,
                success=True,
                errors=[]
            )
            
        except Computer.DoesNotExist:
            return UpdateComputerMutation(
                computer=None,
                success=False,
                errors=["Ordinateur non trouvé"]
            )
        except Exception as e:
            return UpdateComputerMutation(
                computer=None,
                success=False,
                errors=[str(e)]
            )


class CreateSoftwareMutation(graphene.Mutation):
    """Mutation pour créer un logiciel"""
    
    class Arguments:
        input = SoftwareInput(required=True)
    
    software = graphene.Field(SoftwareType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, input):
        try:
            # Récupérer l'ordinateur
            computer = Computer.objects.get(id=input.computerId)
            
            # Créer le logiciel
            software, created = Software.get_or_create_software(computer, {
                'name': input.name,
                'version': input.version or 'Unknown',
                'publisher': input.publisher or 'Unknown',
                'install_date': input.installDate or 'Unknown',
                'detection_date': input.detectionDate or timezone.now()
            })
            
            return CreateSoftwareMutation(
                software=software,
                success=True,
                errors=[]
            )
            
        except Computer.DoesNotExist:
            return CreateSoftwareMutation(
                software=None,
                success=False,
                errors=["Ordinateur non trouvé"]
            )
        except Exception as e:
            return CreateSoftwareMutation(
                software=None,
                success=False,
                errors=[str(e)]
            )


class UpdateSoftwareMutation(graphene.Mutation):
    """Mutation pour mettre à jour un logiciel"""
    
    class Arguments:
        id = graphene.ID(required=True)
        input = SoftwareInput(required=True)
    
    software = graphene.Field(SoftwareType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, id, input):
        try:
            # Récupérer le logiciel
            software = Software.objects.get(id=id)
            
            # Mettre à jour le logiciel
            software.name = input.name
            software.version = input.version or software.version
            software.publisher = input.publisher or software.publisher
            software.install_date = input.installDate or software.install_date
            software.detection_date = input.detectionDate or timezone.now()
            software.save()
            
            return UpdateSoftwareMutation(
                software=software,
                success=True,
                errors=[]
            )
            
        except Software.DoesNotExist:
            return UpdateSoftwareMutation(
                software=None,
                success=False,
                errors=["Logiciel non trouvé"]
            )
        except Exception as e:
            return UpdateSoftwareMutation(
                software=None,
                success=False,
                errors=[str(e)]
            )


class Query(graphene.ObjectType):
    """Queries GraphQL"""
    
    # Queries pour les ordinateurs
    all_computers = graphene.List(ComputerType)
    computer = graphene.Field(ComputerType, id=graphene.ID())
    computer_by_serial = graphene.Field(ComputerType, serial_number=graphene.String())
    
    # Queries pour les logiciels
    all_software = graphene.List(SoftwareType)
    software = graphene.Field(SoftwareType, id=graphene.ID())
    computer_software = graphene.List(SoftwareType, computer_id=graphene.Int())
    
    # Queries pour les logs
    all_logs = graphene.List(InventoryLogType)
    computer_logs = graphene.List(InventoryLogType, computer_id=graphene.Int())
    
    def resolve_all_computers(self, info):
        return Computer.objects.all()
    
    def resolve_computer(self, info, id):
        return Computer.objects.get(id=id)
    
    def resolve_computer_by_serial(self, info, serial_number):
        return Computer.objects.get(serial_number=serial_number)
    
    def resolve_all_software(self, info):
        return Software.objects.all()
    
    def resolve_software(self, info, id):
        return Software.objects.get(id=id)
    
    def resolve_computer_software(self, info, computer_id):
        return Software.objects.filter(computer_id=computer_id)
    
    def resolve_all_logs(self, info):
        return InventoryLog.objects.all()
    
    def resolve_computer_logs(self, info, computer_id):
        return InventoryLog.objects.filter(computer_id=computer_id)


class Mutation(graphene.ObjectType):
    """Mutations GraphQL"""
    
    create_computer = CreateComputerMutation.Field()
    update_computer = UpdateComputerMutation.Field()
    create_software = CreateSoftwareMutation.Field()
    update_software = UpdateSoftwareMutation.Field()


# Créer le schéma
schema = graphene.Schema(query=Query, mutation=Mutation)

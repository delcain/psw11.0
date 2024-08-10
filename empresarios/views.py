from django.shortcuts import render, HttpResponse, redirect
from django.urls import reverse
from .models import Empresas, Documento, Metricas
from investidores.models import PropostaInvestimento
from usuarios.views import logar
from django.contrib import messages
from django.contrib.messages import constants

# Create your views here.

def cadastrar_empresa(request):
    if not request.user.is_authenticated:
        return redirect(logar)
    
    if request.method == "GET":
        
        return render(request, 'cadastrar_empresa.html', 
                      {'tempo_existencia': Empresas.tempo_existencia_choices,
                       'area':Empresas.area_choices,
                       })
    
    elif request.method == "POST":
        nome = request.POST.get('nome')
        cnpj = request.POST.get('cnpj')
        site = request.POST.get('site')
        tempo_existencia = request.POST.get('tempo_existencia')
        descricao = request.POST.get('descricao')
        data_final_captacao = request.POST.get('data_final_captacao')
        percentual_equity = request.POST.get('percentual_equity')
        estagio = request.POST.get('estagio')
        area = request.POST.get('area')
        publico_alvo = request.POST.get('publico_alvo')
        valor = request.POST.get('valor')
        pitch = request.FILES.get('pitch')
        logo = request.FILES.get('logo')

        # Todo: Realizar validação de campos.

        try:
            empresa = Empresas(
                user=request.user,
                nome = nome,
                cnpj = cnpj,
                site = site,
                tempo_existencia = tempo_existencia,
                descricao = descricao,
                data_final_captacao = data_final_captacao,
                percentual_equity = percentual_equity,
                estagio = estagio,
                area = area,
                publico_alvo = publico_alvo,
                valor = valor,
                pitch = pitch,
                logo = logo,
            )
            empresa.save()
        except:
            messages.add_message(request, constants.ERROR, 'Não foi possível salvar esse formulário no banco de dados.')

    messages.add_message(request, constants.SUCCESS, 'Empresa cadastrada com sucesso.')
    return redirect(cadastrar_empresa)

def listar_empresas(request):
    if not request.user.is_authenticated:
        return redirect(logar)
    
    if request.method == "GET":
        # TODO: Realizar os filtros das empresas
        empresas = Empresas.objects.filter(user=request.user)
        return render(request, 'listar_empresas.html', {'empresas':empresas})

def empresa(request, id):
    empresa = Empresas.objects.get(id=id)
    
    if empresa.user != request.user:
         messages.add_message(request, constants.ERROR, 'Erro fatal! ID usuário empresa ! Request User')
         return redirect(logar)
    
    if request.method == "GET":
        empresa = Empresas.objects.get(id=id)
        documentos = Documento.objects.filter(empresa=empresa)
        
        pi = PropostaInvestimento.objects.filter(empresa=empresa)
        pi_enviada = PropostaInvestimento.objects.filter(status='PE')

        percentual_vendido = 0
        
        for p in pi:
             if p.status == 'PA':
                  percentual_vendido = percentual_vendido + p.percentual
                  
        total_capitado = sum(pi.filter(status='PA').values_list('valor', flat=True))

        valuation = (100 * float(total_capitado)) / float(percentual_vendido) if percentual_vendido != 0 else 0
        

        return render(request, 'empresa.html', {'empresa':empresa, 'documentos':documentos,'pi':pi, 'pi_enviada':pi_enviada,'percentual_vendido':int(percentual_vendido), 'total_capitado':total_capitado, 'valuation':valuation })
    return HttpResponse('ok')

def add_doc(request, id):
    empresa = Empresas.objects.get(id=id)
    titulo = request.POST.get('titulo')
    arquivo = request.FILES.get('arquivo')
    extensao = arquivo.name.split('.') 
    # Aceita somente arquivos PDF
    if extensao[1] != 'pdf':
            messages.add_message(request, constants.ERROR, 'Envei somente arquivos em PDF')
            return redirect('empresa', id=id)

    # Verifica se anexo está presente.
    if not arquivo:
            messages.add_message(request, constants.ERROR, 'Envio não pode ser vazio.')
            return redirect('empresa', id=id)
  
    documento = Documento(
        empresa=empresa,
        titulo=titulo,
        arquivo=arquivo,
    )
    documento.save()
    messages.add_message(request, constants.SUCCESS, 'Arquivo salvo com sucesso.')
    return redirect('empresa', id=id)

def excluir_dc(request, id):
     documento = Documento.objects.get(id=id)

     if documento.empresa.user != request.user:
          messages.add_message(request, constants.ERROR, 'Esse documento não é seu.')
          return redirect('empresa', id=id)
     
     documento.delete()
     messages.add_message(request, constants.SUCCESS, 'Arquivo apagado com sucesso.')
     return redirect('empresa', id=documento.empresa.id)

def add_metrica(request, id):
     empresa = Empresas.objects.get(id=id)
     titulo = request.POST.get('titulo')
     valor = request.POST.get('valor')

     metrica = Metricas(
          empresa=empresa,
          titulo=titulo,
          valor=valor
     )
     metrica.save()
     messages.add_message(request, constants.SUCCESS, 'Metrica cadastrada com sucesso.')
     return redirect('empresa', id=id)

def gerenciar_proposta(request, id):
    acao = request.GET.get('acao')
    pi = PropostaInvestimento.objects.get(id=id)
    
    if acao == 'aceitar':
        messages.add_message(request, constants.SUCCESS, 'Proposta aceita.')
        pi.status = 'PA'

    elif acao == 'negar':
        messages.add_message(request, constants.SUCCESS, 'Proposta recusada.')
        pi.status = 'PR'

    pi.save()          
    
    return redirect('empresa', pi.empresa.id)

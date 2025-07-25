from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from schemas import PedidoSchema, ItemPedidoSchema, ResponsePedidoSchema
from models import Pedido, Usuario, ItemPedido
from typing import List

order_router = APIRouter(prefix="/pedidos", tags=["pedidos"], dependencies=[Depends(verificar_token)])

@order_router.get("/")
async def pedidos():
    """
    Rota de verificação do serviço de pedidos
    
    Esta rota serve para verificar se o serviço de pedidos está funcionando.
    Todas as rotas de pedidos requerem autenticação JWT válida.
    
    Returns:
        dict: Mensagem de confirmação do acesso ao serviço de pedidos
    
    Security:
        Requer token JWT válido no header Authorization
    """
    return {"mensagem": "Você acessou a rota de pedidos"}

@order_router.post("/criar-pedido")
async def criar_pedido(pedido_schema: PedidoSchema, session: Session = Depends(pegar_sessao)):
    """
    Criar novo pedido no sistema
    
    Cria um novo pedido com status inicial "PENDENTE" para o usuário especificado.
    O pedido é criado vazio e itens devem ser adicionados posteriormente.
    
    Args:
        pedido_schema (PedidoSchema): Dados do pedido
            - usuario: ID do usuário que está fazendo o pedido
    
    Returns:
        dict: Confirmação da criação com ID do pedido
            - mensagem: Mensagem de sucesso
            - ID do pedido criado
    
    Security:
        Requer token JWT válido no header Authorization
    
    Note:
        O pedido é criado com preço inicial 0.0 e status "PENDENTE"
    """
    novo_pedido = Pedido(usuario=pedido_schema.usuario)
    session.add(novo_pedido)
    session.commit()
    return {"mensagem": f"Pedido Criado Com Sucesso. ID do Pedido: {novo_pedido.id}"}

@order_router.post("/cancelar/{id_pedido}")
async def cancelar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    """
    Cancelar pedido existente
    
    Altera o status de um pedido para "CANCELADO". Apenas o dono do pedido
    ou um administrador podem cancelar um pedido.
    
    Args:
        id_pedido (int): ID do pedido a ser cancelado
        usuario (Usuario): Usuário autenticado (obtido do token)
    
    Returns:
        dict: Confirmação do cancelamento
            - mensagem: Mensagem de sucesso
            - pedido: Dados atualizados do pedido
    
    Raises:
        HTTPException: 400 - Pedido não encontrado
        HTTPException: 401 - Usuário sem autorização para esta operação
    
    Security:
        Requer token JWT válido no header Authorization
        Apenas o dono do pedido ou administradores podem cancelar
    """
    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido Não Encontrado")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você Não Tem Autorização Para Fazer Essa Operação")
    pedido.status = "CANCELADO"
    session.commit()
    return {
        "mensagem": f"Pedido Número: {id_pedido} Cancelado Com Sucesso", 
        "pedido": pedido
    }

@order_router.get("/listar")
async def listar_pedidos(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    """
    Listar todos os pedidos do sistema (apenas administradores)
    
    Retorna uma lista completa de todos os pedidos no sistema.
    Esta operação é restrita apenas a usuários administradores.
    
    Args:
        usuario (Usuario): Usuário autenticado (obtido do token)
    
    Returns:
        dict: Lista de todos os pedidos
            - pedidos: Array com todos os pedidos do sistema
    
    Raises:
        HTTPException: 401 - Usuário não é administrador
    
    Security:
        Requer token JWT válido no header Authorization
        Requer privilégios de administrador
    """
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você Não Tem Autorização Para Fazer Essa Operação")
    else:
        pedidos = session.query(Pedido).all()
        return {
            "pedidos": pedidos
        }
    
@order_router.post("/adicionar-item/{id_pedido}")
async def adicionar_item_pedido(id_pedido: int, item_pedido_schema: ItemPedidoSchema, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    """
    Adicionar item (pizza) a um pedido existente
    
    Adiciona um novo item ao pedido especificado. O preço total do pedido
    é recalculado automaticamente após a adição do item.
    
    Args:
        id_pedido (int): ID do pedido onde adicionar o item
        item_pedido_schema (ItemPedidoSchema): Dados do item a ser adicionado
            - quantidade: Quantidade de pizzas deste tipo
            - sabor: Sabor da pizza (ex: "Margherita", "Pepperoni")
            - tamanho: Tamanho da pizza (ex: "Pequena", "Média", "Grande")
            - preco_unitario: Preço unitário da pizza
        usuario (Usuario): Usuário autenticado (obtido do token)
    
    Returns:
        dict: Confirmação da adição do item
            - mensagem: Mensagem de sucesso
            - item_id: ID do item criado
            - preco_pedido: Novo preço total do pedido
    
    Raises:
        HTTPException: 400 - Pedido não existe
        HTTPException: 401 - Usuário sem autorização para esta operação
    
    Security:
        Requer token JWT válido no header Authorization
        Apenas o dono do pedido ou administradores podem adicionar itens
    """
    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()

    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido Não Existe")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você Não Tem Autorização Para Fazer Essa Operação")
    item_pedido = ItemPedido(item_pedido_schema.quantidade, item_pedido_schema.sabor, item_pedido_schema.tamanho, item_pedido_schema.preco_unitario, id_pedido)
    session.add(item_pedido)
    pedido.calcular_preco()
    session.commit()
    return {
        "mensagem": "Item Criado Com Sucesso",
        "item_id": item_pedido.id,
        "preco_pedido": pedido.preco
    }

@order_router.post("/remover-item/{id_item_pedido}")
async def remover_item_pedido(id_item_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    """
    Remover item específico de um pedido
    
    Remove um item específico do pedido. O preço total do pedido
    é recalculado automaticamente após a remoção do item.
    
    Args:
        id_item_pedido (int): ID do item a ser removido
        usuario (Usuario): Usuário autenticado (obtido do token)
    
    Returns:
        dict: Confirmação da remoção do item
            - mensagem: Mensagem de sucesso
            - quantidade_itens_pedido: Nova quantidade de itens no pedido
            - pedido: Dados atualizados do pedido
    
    Raises:
        HTTPException: 400 - Item do pedido não existe
        HTTPException: 401 - Usuário sem autorização para esta operação
    
    Security:
        Requer token JWT válido no header Authorization
        Apenas o dono do pedido ou administradores podem remover itens
    """
    item_pedido = session.query(ItemPedido).filter(ItemPedido.id==id_item_pedido).first()
    pedido = session.query(Pedido).filter(Pedido.id==id_item_pedido).first()
    if not item_pedido:
        raise HTTPException(status_code=400, detail="Item do Pedido Não Existe")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você Não Tem Autorização Para Fazer Essa Operação")
    session.delete(item_pedido)
    pedido.calcular_preco()
    session.commit()
    return {
        "mensagem": "Item Removido Com Sucesso",
        "quantidade_itens_pedido": len(pedido.itens),
        "pedido": pedido
    }

@order_router.post("/finalizar/{id_pedido}")
async def finalizar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    """
    Finalizar pedido existente
    
    Altera o status de um pedido para "FINALIZADO", indicando que o pedido
    foi processado e entregue. Apenas o dono do pedido ou um administrador
    podem finalizar um pedido.
    
    Args:
        id_pedido (int): ID do pedido a ser finalizado
        usuario (Usuario): Usuário autenticado (obtido do token)
    
    Returns:
        dict: Confirmação da finalização
            - mensagem: Mensagem de sucesso
            - pedido: Dados atualizados do pedido
    
    Raises:
        HTTPException: 400 - Pedido não encontrado
        HTTPException: 401 - Usuário sem autorização para esta operação
    
    Security:
        Requer token JWT válido no header Authorization
        Apenas o dono do pedido ou administradores podem finalizar
    """
    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido Não Encontrado")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você Não Tem Autorização Para Fazer Essa Operação")
    pedido.status = "FINALIZADO"
    session.commit()
    return {
        "mensagem": f"Pedido Número: {id_pedido} Finalizado Com Sucesso", 
        "pedido": pedido
    }

@order_router.get("/pedido/{id_pedido}")
async def visualizar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    """
    Visualizar detalhes de um pedido específico
    
    Retorna informações detalhadas de um pedido específico, incluindo
    todos os itens associados. Apenas o dono do pedido ou administradores
    podem visualizar os detalhes.
    
    Args:
        id_pedido (int): ID do pedido a ser visualizado
        usuario (Usuario): Usuário autenticado (obtido do token)
    
    Returns:
        dict: Detalhes completos do pedido
            - quantidade_tens_pedido: Número total de itens no pedido
            - pedido: Dados completos do pedido incluindo itens
    
    Raises:
        HTTPException: 400 - Pedido não encontrado
        HTTPException: 401 - Usuário sem autorização para esta operação
    
    Security:
        Requer token JWT válido no header Authorization
        Apenas o dono do pedido ou administradores podem visualizar
    """
    pedido = session.query(Pedido).filter(Pedido.id==id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido Não Encontrado")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você Não Tem Autorização Para Fazer Essa Operação")
    return {
        "quantidade_tens_pedido": len(pedido.itens),
        "pedido": pedido
    }

@order_router.get("/pedidos-usuario", response_model=List[ResponsePedidoSchema])
async def listar_pedidos_usuario(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    """
    Listar pedidos do usuário autenticado
    
    Retorna todos os pedidos pertencentes ao usuário autenticado,
    incluindo detalhes completos de cada pedido e seus itens.
    
    Args:
        usuario (Usuario): Usuário autenticado (obtido do token)
    
    Returns:
        List[ResponsePedidoSchema]: Lista de pedidos do usuário
            Cada pedido contém:
            - id: ID do pedido
            - status: Status atual (PENDENTE/CANCELADO/FINALIZADO)
            - preco: Preço total do pedido
            - itens: Lista de itens do pedido com detalhes
    
    Security:
        Requer token JWT válido no header Authorization
        Retorna apenas pedidos do usuário autenticado
    
    Note:
        A resposta segue o modelo ResponsePedidoSchema para consistência
    """
    pedidos = session.query(Pedido).filter(Pedido.usuario==usuario.id).all()
    return pedidos

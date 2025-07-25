from fastapi import APIRouter, Depends, HTTPException
from models import Usuario
from dependencies import pegar_sessao, verificar_token
from main import bcrypt_context, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from schemas import UsuarioSchema, LoginSchema
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm

def criar_token(id_usuario, duracao_token=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    data_expiracao = datetime.now(timezone.utc) + duracao_token
    dic_info = {
        "sub": str(id_usuario),
        "exp": data_expiracao
    }
    jwt_codificado = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)
    return jwt_codificado
    

def autenticar_usuario(email, senha, session):
    usuario = session.query(Usuario).filter(Usuario.email==email).first()
    if not usuario:
        return False
    elif not bcrypt_context.verify(senha, usuario.senha):
        return False
    return usuario

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.get("/")
async def home():
    """
    Rota de verificação do serviço de autenticação
    
    Esta rota serve para verificar se o serviço de autenticação está funcionando.
    Não requer autenticação e retorna informações básicas sobre o status do serviço.
    
    Returns:
        dict: Mensagem de confirmação e status de autenticação
    """
    return {"mensagem": "Você acessou a rota de autenticação", "autenticado": False}

@auth_router.post("/criar-conta")
async def criar_conta(usuario_schema:UsuarioSchema, session: Session = Depends(pegar_sessao)):
    """
    Cadastrar novo usuário no sistema
    
    Cria uma nova conta de usuário no sistema. O email deve ser único e a senha
    será automaticamente criptografada usando bcrypt antes de ser armazenada.
    
    Args:
        usuario_schema (UsuarioSchema): Dados do usuário a ser cadastrado
            - nome: Nome completo do usuário
            - email: Email único do usuário (será validado)
            - senha: Senha em texto plano (será criptografada)
            - ativo: Status ativo do usuário (opcional, padrão: True)
            - admin: Se o usuário é administrador (opcional, padrão: False)
    
    Returns:
        dict: Mensagem de confirmação do cadastro
    
    Raises:
        HTTPException: 400 - Email já cadastrado no sistema
    """
    usuario = session.query(Usuario).filter(Usuario.email==usuario_schema.email).first()

    if usuario:
        raise HTTPException(status_code=400, detail="Email Já Cadastrado!")
    else:
        senha_criptografada = bcrypt_context.hash(usuario_schema.senha)
        novo_usuario = Usuario(usuario_schema.nome, usuario_schema.email, senha_criptografada, usuario_schema.ativo, usuario_schema.admin)
        session.add(novo_usuario)
        session.commit()
        return {"message": f"Email {usuario_schema.email} Cadastrado Com Sucesso!"}
    
@auth_router.post("/login")
async def login(login_schema: LoginSchema, session: Session = Depends(pegar_sessao)):
    """
    Autenticar usuário e gerar tokens JWT
    
    Autentica um usuário usando email e senha, retornando tokens de acesso
    e refresh para uso nas demais rotas protegidas do sistema.
    
    Args:
        login_schema (LoginSchema): Credenciais de login
            - email: Email do usuário cadastrado
            - senha: Senha em texto plano
    
    Returns:
        dict: Tokens de autenticação
            - access_token: Token JWT para acesso (válido por 30 minutos)
            - refresh_token: Token para renovação (válido por 7 dias)
            - token_type: Tipo do token (Bearer)
    
    Raises:
        HTTPException: 400 - Credenciais inválidas ou usuário não encontrado
    """
    usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)
    
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuário Não Encontrado ou Credenciais Inválidas!")
    else:
        access_token = criar_token(usuario.id)
        refresh_token = criar_token(usuario.id, duracao_token=timedelta(days=7))
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer"   
            }
    
@auth_router.post("/login-form")
async def login_form(dados_formulario: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(pegar_sessao)):
    """
    Login via formulário OAuth2 (compatível com Swagger UI)
    
    Endpoint de login compatível com o padrão OAuth2 Password Flow,
    permitindo autenticação direta através da interface do Swagger UI.
    Utiliza username (email) e password para autenticação.
    
    Args:
        dados_formulario (OAuth2PasswordRequestForm): Formulário OAuth2
            - username: Email do usuário (campo username do OAuth2)
            - password: Senha do usuário
    
    Returns:
        dict: Token de acesso
            - access_token: Token JWT para acesso (válido por 30 minutos)
            - token_type: Tipo do token (Bearer)
    
    Raises:
        HTTPException: 400 - Credenciais inválidas ou usuário não encontrado
    
    Note:
        Este endpoint é usado pelo Swagger UI para autenticação automática
    """
    usuario = autenticar_usuario(dados_formulario.username, dados_formulario.password, session)
    
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuário Não Encontrado ou Credenciais Inválidas!")
    else:
        access_token = criar_token(usuario.id)
        return {
            "access_token": access_token,
            "token_type": "Bearer"   
            }

    
@auth_router.get("/refresh")
async def use_refresh_token(usuario: Usuario = Depends(verificar_token)):
    """
    Renovar token de acesso usando token atual
    
    Gera um novo token de acesso para o usuário autenticado.
    Útil para manter a sessão ativa sem precisar fazer login novamente.
    
    Args:
        usuario (Usuario): Usuário autenticado (obtido do token atual)
    
    Returns:
        dict: Novo token de acesso
            - access_token: Novo token JWT (válido por 30 minutos)
            - token_type: Tipo do token (Bearer)
    
    Raises:
        HTTPException: 401 - Token inválido ou expirado
    
    Security:
        Requer token JWT válido no header Authorization
    """
    access_token = criar_token(usuario.id)
    return {
        "access_token": access_token,
        "token_type": "Bearer"   
        }

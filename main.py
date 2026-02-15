from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Category, Product

# Create tables
Base.metadata.create_all(bind=engine)

from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Campeão do Churrasco")
app.mount("/static", StaticFiles(directory="."), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/admin/toggle/{product_id}")
def toggle_product_availability(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        product.is_available = not product.is_available
        db.commit()
        return {"status": "success", "is_available": product.is_available}
    return {"status": "error", "message": "Product not found"}

# Helper to render Logo (SVG)
def render_logo(size="md", classes=""):
    size_classes = {
        "sm": "w-12 h-12",
        "md": "w-20 h-20",
        "lg": "w-32 h-32"
    }
    s_class = size_classes.get(size, "w-20 h-20")
    
    return f"""
    <div class="relative flex items-center justify-center bg-brand-blue shadow-xl overflow-hidden rounded-xl {s_class} {classes}">
      <svg viewBox="0 0 100 100" class="w-[90%] h-[90%] select-none" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <path id="textArc" d="M 20,48 A 30,30 0 0,1 80,48" fill="none" />
        </defs>
        <text class="fill-white font-bold" style="font-size: 9px; letter-spacing: 0.12em">
          <textPath href="#textArc" startOffset="50%" text-anchor="middle">CAMPEÃO</textPath>
        </text>
        <text x="50" y="48" text-anchor="middle" class="fill-white font-bold" style="font-size: 5.5px; letter-spacing: 0.05em">DO</text>
        <text x="50" y="62" text-anchor="middle" class="fill-white font-black" style="font-size: 13.5px; letter-spacing: -0.02em">CHURRASCO</text>
        <line x1="22" y1="67" x2="78" y2="67" stroke="white" stroke-width="1.2" />
        <text x="50" y="74" text-anchor="middle" class="fill-white font-bold" style="font-size: 4.8px; letter-spacing: 0.15em">DESDE 1980</text>
      </svg>
    </div>
    """

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    products = db.query(Product).all()

    # Pre-process data for the view
    # Structure: categories_data = [ { 'category': cat_obj, 'products': [prod_obj, ...] } ]
    categories_data = []
    for cat in categories:
        prods = [p for p in products if p.category_id == cat.id]
        categories_data.append({"category": cat, "products": prods})

    # Default active tab (first one)
    first_cat_id = categories[0].id if categories else 0

    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR" class="scroll-smooth">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Campeão do Churrasco | A Arte da Brasa em Mogi Mirim</title>
        
        <!-- Fonts -->
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Montserrat:wght@300;400;600;700&display=swap" rel="stylesheet">
        
        <!-- Tailwind CSS & Config -->
        <script src="https://cdn.tailwindcss.com"></script>
        <script>
          tailwind.config = {{
            darkMode: 'class',
            theme: {{
              extend: {{
                colors: {{
                  'rich-black': '#FFFFFF', 
                  'brand-blue': '#0090FF', 
                  'brand-blue-light': '#E0F2FF', 
                  'steak-gold': '#D4AF37',
                  'smoke-grey': '#F3F4F6', 
                  'dark-text': '#0D0D0D', 
                  'medium-text': '#4B5563',
                }},
                fontFamily: {{
                  bebas: ['"Bebas Neue"', 'cursive'],
                  montserrat: ['Montserrat', 'sans-serif'],
                }},
                animation: {{
                  'shimmer': 'shimmer 3s infinite linear',
                  'fadeIn': 'fadeIn 0.5s ease-out',
                }},
                keyframes: {{
                  shimmer: {{
                    '0%': {{ transform: 'translateX(-100%)' }},
                    '100%': {{ transform: 'translateX(100%)' }},
                  }},
                  fadeIn: {{
                    '0%': {{ opacity: '0', transform: 'translateY(10px)' }},
                    '100%': {{ opacity: '1', transform: 'translateY(0)' }},
                  }}
                }}
              }}
            }}
          }}
        </script>
        
        <!-- GSAP -->
        <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js"></script>

        <style>
          .glass-shimmer::after {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 50%;
            height: 100%;
            background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.4), transparent);
            transform: skewX(-25deg);
            animation: shimmer 4s infinite;
          }}
          .tab-content {{ display: none; }}
          .tab-content.active {{ display: block; }}
          
          /* Dark Mode Overrides */
          .dark .rich-black-bg {{ background-color: #0a0a0a; }}
          .dark .dark-text-color {{ color: #f3f4f6; }}
          .dark .nav-glass {{ background-color: rgba(15, 15, 15, 0.8); border-color: rgba(255, 255, 255, 0.05); }}
        </style>
        <script>
            // Check theme on load
            if (localStorage.getItem('theme') === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {{
                document.documentElement.classList.add('dark');
            }} else {{
                document.documentElement.classList.remove('dark');
            }}
        </script>
    </head>
    <body class="bg-rich-black dark:bg-neutral-950 text-dark-text dark:text-neutral-100 font-montserrat overflow-x-hidden selection:bg-brand-blue selection:text-white transition-colors duration-300">

        <!-- NAVBAR -->
        <nav class="fixed top-0 left-0 w-full z-[100] bg-white/80 dark:bg-neutral-900/80 backdrop-blur-xl border-b border-black/5 dark:border-white/5 py-3 md:py-4 px-6 md:px-12 flex justify-between items-center shadow-sm transition-colors duration-300">
          <div class="flex items-center gap-3 group cursor-pointer relative z-[110]">
            {render_logo(size="sm", classes="md:w-20 md:h-20 transition-transform group-hover:scale-105 shadow-brand-blue/10 shadow-lg")}
            <div class="flex flex-col">
              <span class="font-bebas text-xl md:text-2xl tracking-wider leading-none text-dark-text dark:text-white">Campeão do Churrasco</span>
              <span class="text-[9px] md:text-[10px] text-brand-blue tracking-[0.2em] font-bold uppercase leading-none mt-1">Tradição desde 1980</span>
            </div>
          </div>
          <div class="flex gap-4 md:gap-10 items-center uppercase text-[11px] font-bold tracking-[0.3em] text-dark-text/80 dark:text-white/80">
            <div class="hidden md:flex gap-10">
              <a href="#hero" class="hover:text-brand-blue transition-all relative group">Início<span class="absolute -bottom-1 left-0 w-0 h-[2px] bg-brand-blue transition-all group-hover:w-full"></span></a>
              <a href="#menu" class="hover:text-brand-blue transition-all relative group">Cardápio<span class="absolute -bottom-1 left-0 w-0 h-[2px] bg-brand-blue transition-all group-hover:w-full"></span></a>
              <a href="#location" class="hover:text-brand-blue transition-all relative group">Localização<span class="absolute -bottom-1 left-0 w-0 h-[2px] bg-brand-blue transition-all group-hover:w-full"></span></a>
            </div>

            <!-- SETTINGS/DARK MODE TOGGLE -->
            <div class="relative group/settings">
              <button id="settings-btn" class="p-2.5 bg-neutral-100 dark:bg-neutral-800 rounded-full hover:bg-neutral-200 dark:hover:bg-neutral-700 transition-all active:scale-95 shadow-inner">
                <svg class="w-5 h-5 text-dark-text dark:text-white transition-transform duration-500 group-hover/settings:rotate-180" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </button>
              
              <div id="settings-menu" class="absolute right-0 mt-3 w-56 bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-2xl shadow-2xl p-4 opacity-0 invisible translate-y-2 transition-all duration-300 group-hover/settings:opacity-100 group-hover/settings:visible group-hover/settings:translate-y-0">
                <p class="text-[10px] text-neutral-400 font-bold uppercase tracking-widest mb-4 px-1">Configurações</p>
                <div class="flex items-center justify-between p-2 hover:bg-neutral-50 dark:hover:bg-neutral-800 rounded-xl transition-colors cursor-pointer group/toggle" onclick="toggleDarkMode()">
                  <span class="text-xs text-dark-text dark:text-neutral-300 font-semibold group-hover/toggle:text-brand-blue transition-colors">Modo Escuro</span>
                  <div class="w-10 h-5 bg-neutral-200 dark:bg-neutral-700 rounded-full relative transition-colors duration-300 dark:bg-brand-blue/30">
                    <div id="theme-toggle-dot" class="absolute top-1 left-1 w-3 h-3 bg-white dark:bg-brand-blue rounded-full transition-all duration-300 translate-x-0 dark:translate-x-5 shadow-sm"></div>
                  </div>
                </div>
                
                <div class="h-[1px] bg-neutral-100 dark:bg-neutral-800 my-2"></div>
                
                <!-- ADMIN LOGIN -->
                <div id="admin-login-section">
                    <div class="flex items-center justify-between p-2 hover:bg-neutral-50 dark:hover:bg-neutral-800 rounded-xl transition-colors cursor-pointer group/admin" onclick="showAdminLogin()">
                      <span class="text-xs text-dark-text dark:text-neutral-300 font-semibold group-hover/admin:text-brand-blue transition-colors">Modo Administrativo</span>
                      <svg class="w-4 h-4 text-neutral-400 group-hover/admin:text-brand-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
                    </div>
                </div>
                <div id="admin-active-section" class="hidden">
                    <div class="flex items-center justify-between p-2 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-xl transition-colors cursor-pointer group/logout" onclick="logoutAdmin()">
                      <span class="text-xs text-red-600 dark:text-red-400 font-semibold">Sair do Admin</span>
                      <svg class="w-4 h-4 text-red-600 dark:text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
                    </div>
                </div>
              </div>
            </div>
          </div>
        </nav>
        
        <!-- ADMIN LOGIN MODAL -->
        <div id="admin-modal" class="fixed inset-0 z-[200] hidden bg-black/60 backdrop-blur-sm flex items-center justify-center p-6">
            <div class="bg-white dark:bg-neutral-900 w-full max-w-md rounded-3xl shadow-2xl p-8 transform transition-all animate-fadeIn">
                <div class="text-center mb-8">
                    <div class="w-16 h-16 bg-brand-blue/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
                        <svg class="w-8 h-8 text-brand-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
                    </div>
                    <h3 class="font-bebas text-3xl text-dark-text dark:text-white uppercase tracking-wider">Acesso Administrativo</h3>
                    <p class="text-sm text-neutral-400 font-medium">Insira o código de acesso para gerenciar o site</p>
                </div>
                <div class="space-y-6">
                    <div>
                        <input type="password" id="admin-password" class="w-full bg-neutral-100 dark:bg-neutral-800 border-0 rounded-2xl p-4 text-center text-2xl tracking-[0.5em] focus:ring-2 focus:ring-brand-blue transition-all dark:text-white" placeholder="••••">
                    </div>
                    <div class="flex gap-4">
                        <button onclick="closeAdminModal()" class="flex-1 py-4 text-xs font-bold uppercase tracking-[0.2em] text-neutral-400 hover:text-dark-text dark:hover:text-white transition-colors">Cancelar</button>
                        <button onclick="attemptAdminLogin()" class="flex-1 bg-brand-blue text-white py-4 rounded-2xl text-xs font-bold uppercase tracking-[0.2em] hover:bg-brand-blue/90 shadow-lg shadow-brand-blue/20 transition-all active:scale-95">Entrar</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- HERO -->
        <section id="hero" class="relative min-h-screen flex items-center justify-center pt-24 overflow-hidden bg-white dark:bg-neutral-950 transition-colors duration-300">
            <div class="absolute inset-0 z-0">
                <img src="https://images.unsplash.com/photo-1594041680534-e8c8cdebd679?auto=format&fit=crop&q=80&w=2000&keyword=brazilian+skewers+grill" 
                     alt="Espetinhos na Brasa" class="w-full h-full object-cover opacity-60 dark:opacity-40 scale-105" />
                <div class="absolute inset-0 bg-gradient-to-t from-brand-blue-light/70 dark:from-neutral-950/90 via-white/80 dark:via-neutral-900/60 to-white/20 dark:to-transparent"></div>
                <div class="absolute inset-0 bg-gradient-to-b from-white/90 dark:from-neutral-950/90 via-transparent to-brand-blue-light/40 dark:to-neutral-900/20"></div>
                <!-- Sky Glow Accent -->
                <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full bg-[radial-gradient(circle_at_center,_rgba(0,144,255,0.1)_0%,_transparent_70%)] dark:bg-[radial-gradient(circle_at_center,_rgba(0,144,255,0.05)_0%,_transparent_70%)]"></div>
            </div>

            <div class="relative z-10 container mx-auto px-6 text-center">
                <div class="inline-flex items-center gap-2 px-6 py-2 border border-brand-blue/30 dark:border-brand-blue/20 text-brand-blue text-[10px] md:text-xs font-bold tracking-[0.4em] uppercase mb-10 bg-brand-blue/5 backdrop-blur-md rounded-full">
                    A AUTÊNTICA TRADIÇÃO DA BRASA
                </div>
                
                <h1 id="hero-title" class="font-bebas text-[clamp(2.5rem,12vw,8rem)] leading-[0.85] mb-8 text-dark-text dark:text-neutral-100 drop-shadow-sm">
                   O CAMPEÃO DO<br/>
                   <span class="text-transparent bg-clip-text bg-gradient-to-r from-brand-blue via-steak-gold to-brand-blue dark:from-brand-blue dark:via-steak-gold dark:to-brand-blue">CHURRASCO</span>
                </h1>
                
                <p id="hero-subtitle" class="max-w-2xl mx-auto text-base md:text-2xl text-dark-text/70 dark:text-neutral-300/70 font-light leading-relaxed mb-16 px-4">
                   Sinta o aroma, <span class="text-brand-blue font-bold">reúna quem você ama.</span> A tradição de Mogi Mirim em um ambiente feito para sua família.
                </p>

                <div id="hero-indicator" class="flex flex-col items-center gap-4">
                   <div class="h-20 w-[1px] bg-gradient-to-b from-transparent via-brand-blue to-transparent"></div>
                   <span class="text-dark-text/40 dark:text-neutral-500 font-bold uppercase tracking-[0.4em] text-[10px] md:text-xs">Deslize para ver o cardápio</span>
                   <div class="animate-bounce mt-2">
                     <svg class="w-6 h-6 text-brand-blue/60" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
                   </div>
                </div>
            </div>
        </section>

        <!-- MENU SECTION -->
        <section id="menu" class="py-24 md:py-32 relative border-y border-black/5 dark:border-white/5 bg-white dark:bg-neutral-950 bg-[radial-gradient(circle_at_top,_rgba(0,144,255,0.12)_0%,_rgba(224,242,255,0.3)_30%,_rgba(255,255,255,1)_80%)] dark:bg-[radial-gradient(circle_at_top,_rgba(0,144,255,0.08)_0%,_rgba(15,15,15,0.5)_40%,_rgba(10,10,10,1)_80%)] transition-colors duration-300">
            <div class="container mx-auto px-4 md:px-6 relative z-10">
                <div class="text-center mb-16 reveal-on-scroll">
                   <h2 class="font-bebas text-5xl md:text-8xl mb-4 text-dark-text dark:text-neutral-100 uppercase">
                     Saboreie momentos em <span class="text-brand-blue">família.</span>
                   </h2>
                   <div class="w-16 md:w-24 h-1 bg-gradient-to-r from-transparent via-brand-blue to-transparent mx-auto mb-10"></div>
                   
                   <!-- CATEGORY TABS -->
                    <div class="flex flex-wrap justify-center gap-2 bg-brand-blue/5 dark:bg-neutral-900/50 p-1.5 rounded-xl backdrop-blur-md border border-brand-blue/10 dark:border-white/5 max-w-4xl mx-auto mb-6">
                       {''.join([f'''
                       <button onclick="switchTab({item['category'].id})" 
                               id="tab-btn-{item['category'].id}"
                               class="tab-btn flex-1 min-w-[80px] text-[9px] md:text-xs font-bold uppercase tracking-wider px-2 md:px-8 py-3 md:py-4 rounded-lg transition-all duration-300 active:scale-90 {'bg-brand-blue text-white shadow-[0_5px_15px_rgba(0,144,255,0.2)]' if item['category'].id == first_cat_id else 'text-dark-text/40 dark:text-neutral-400 hover:bg-brand-blue/10 hover:text-brand-blue'}">
                         {item['category'].name}
                       </button>
                       ''' for item in categories_data])}
                    </div>
                </div>

                <!-- MENU CONTENT AREAS -->
                {''.join([f'''
                <div id="tab-content-{item['category'].id}" class="tab-content {'active' if item['category'].id == first_cat_id else ''}">
                   <div class="mb-16 last:mb-0">
                      
                       <div class="flex items-center gap-4 md:gap-6 mb-8">
                        <h3 class="font-bebas text-3xl md:text-4xl text-brand-blue tracking-widest uppercase">{item['category'].name}</h3>
                        <div class="flex-grow h-[1px] bg-gradient-to-r from-brand-blue/20 to-transparent"></div>
                      </div>

                      {f'''
                      <!-- SUB-FILTERS FOR BEVERAGES -->
                      <div class="flex flex-wrap gap-2 mb-10 reveal-on-scroll">
                        <button onclick="filterSubCat('all')" class="subcat-btn active px-4 py-2 rounded-lg text-[10px] font-bold uppercase tracking-wider border border-brand-blue/20 transition-all bg-brand-blue text-white">Todos</button>
                        <button onclick="filterSubCat('Cervejas')" class="subcat-btn px-4 py-2 rounded-lg text-[10px] font-bold uppercase tracking-wider border border-brand-blue/20 transition-all text-dark-text/60 dark:text-neutral-400 hover:bg-brand-blue/5">Cervejas</button>
                        <button onclick="filterSubCat('Refrigerantes')" class="subcat-btn px-4 py-2 rounded-lg text-[10px] font-bold uppercase tracking-wider border border-brand-blue/20 transition-all text-dark-text/60 dark:text-neutral-400 hover:bg-brand-blue/5">Refrigerantes</button>
                        <button onclick="filterSubCat('Águas')" class="subcat-btn px-4 py-2 rounded-lg text-[10px] font-bold uppercase tracking-wider border border-brand-blue/20 transition-all text-dark-text/60 dark:text-neutral-400 hover:bg-brand-blue/5">Águas</button>
                      </div>
                      ''' if item['category'].name == 'Bebidas' else ''}

                      <div class="grid grid-cols-2 lg:grid-cols-3 gap-3 md:gap-8 product-grid">
                        {''.join([f'''
                          <div id="product-card-{prod.id}" 
                               data-subcat="{prod.sub_category or ''}"
                               class="product-card reveal-on-scroll group bg-white/60 dark:bg-neutral-900/60 backdrop-blur-md border border-brand-blue/10 dark:border-white/5 overflow-hidden transition-all duration-500 hover:shadow-[0_25px_50px_-12px_rgba(0,144,255,0.15)] hover:border-brand-blue/40 dark:hover:border-brand-blue/40 md:hover:-translate-y-2 rounded-xl flex flex-col relative {'opacity-50 grayscale select-none' if not prod.is_available else ''}">
                             <div class="absolute inset-0 pointer-events-none glass-shimmer opacity-30"></div>
                             
                             <!-- AVAILABILITY INDICATOR -->
                             <div id="status-badge-{prod.id}" class="absolute top-2 left-2 z-20 px-2 py-0.5 rounded text-[8px] md:text-[10px] font-black uppercase tracking-widest shadow-lg transition-all {'bg-red-500 text-white' if not prod.is_available else 'hidden'}">
                                ESGOTADO
                             </div>

                             <!-- ADMIN CONTROLS -->
                             <div class="admin-only hidden absolute top-2 left-2 z-[30] flex gap-2">
                                <button onclick="toggleAvailability({prod.id})" class="p-2 bg-white/90 dark:bg-neutral-800/90 rounded-lg shadow-xl border border-brand-blue/20 hover:scale-110 active:scale-95 transition-all group/admin-btn">
                                    <svg class="w-4 h-4 { 'text-red-500' if prod.is_available else 'text-green-500' }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                                    </svg>
                                    <span class="absolute top-full left-0 mt-1 bg-dark-text text-white text-[8px] px-1 py-0.5 rounded opacity-0 group-hover/admin-btn:opacity-100 whitespace-nowrap">{ 'Desativar' if prod.is_available else 'Ativar' }</span>
                                </button>
                             </div>

                             {f'''<div class="relative aspect-video overflow-hidden">
                                <img src="{prod.image_url}" alt="{prod.name}" class="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-110" />
                                <div class="absolute inset-0 bg-gradient-to-t from-white dark:from-neutral-950 via-transparent to-transparent opacity-40"></div>
                                <div class="absolute top-2 right-2 md:top-4 md:right-4 bg-brand-blue text-white font-bebas text-sm md:text-xl px-2 md:px-4 py-0.5 md:py-1 rounded shadow-lg">R$ {prod.price:.2f}</div>
                             </div>''' if prod.image_url else ''}
                             
                             <div class="p-4 md:p-8 flex flex-col flex-grow {'pt-6 md:pt-10' if not prod.image_url else ''}">
                                <div class="flex flex-col md:flex-row justify-between items-start mb-2 md:mb-3 gap-1 md:gap-4">
                                  <h4 class="font-bebas text-lg md:text-2xl tracking-wide text-dark-text dark:text-neutral-100 group-hover:text-brand-blue transition-colors line-clamp-2">{prod.name}</h4>
                                  {f'<span class="text-brand-blue font-bebas text-base md:text-xl whitespace-nowrap">R$ {prod.price:.2f}</span>' if not prod.image_url else ''}
                                </div>
                                <p class="text-[10px] md:text-xs text-dark-text/50 dark:text-neutral-400 font-light leading-relaxed mb-4 md:mb-6 flex-grow line-clamp-3">{prod.description or ''}</p>

                             </div>
                          </div>
                        ''' for prod in item['products']])}
                      </div>
                      
                      {f"<p class='text-center text-gray-400 italic mt-8'>Nenhum item encontrado nesta categoria.</p>" if not item['products'] else ""}

                   </div>
                </div>
                ''' for item in categories_data])}
            </div>
            <div class="absolute inset-x-0 bottom-0 h-48 bg-gradient-to-t from-brand-blue-light/40 to-transparent pointer-events-none"></div>
        </section>

        <!-- LOCATION -->
        <section id="location" class="py-32 bg-white dark:bg-neutral-950 overflow-hidden relative transition-colors duration-300">
          <div class="absolute top-0 right-0 w-[500px] h-[500px] bg-brand-blue/5 dark:bg-brand-blue/[0.03] blur-[150px] -translate-y-1/2 translate-x-1/2"></div>
          <div class="container mx-auto px-6 relative z-10">
            <div class="flex flex-col lg:flex-row gap-20 items-center">
              <div class="w-full lg:w-1/2 reveal-on-scroll">
                <h2 class="font-bebas text-6xl md:text-8xl mb-8 text-dark-text dark:text-neutral-100">ONDE A <span class="text-brand-blue">BRASA</span> VIVE</h2>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-12">
                   <!-- Address -->
                   <div class="flex gap-5 items-start">
                     <div class="p-4 bg-brand-blue/5 dark:bg-neutral-900 rounded-2xl border border-brand-blue/10 dark:border-white/5"><svg class="w-6 h-6 text-brand-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg></div>
                     <div><h4 class="font-bold text-dark-text dark:text-neutral-400 uppercase text-[10px] tracking-[0.3em] mb-3">Endereço</h4><p class="text-dark-text/50 dark:text-neutral-500 text-sm">Av. 22 de Outubro, 630<br/>Mogi Mirim</p></div>
                   </div>
                   <!-- Time -->
                   <div class="flex gap-5 items-start">
                     <div class="p-4 bg-brand-blue/5 dark:bg-neutral-900 rounded-2xl border border-brand-blue/10 dark:border-white/5"><svg class="w-6 h-6 text-brand-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg></div>
                     <div><h4 class="font-bold text-dark-text dark:text-neutral-400 uppercase text-[10px] tracking-[0.3em] mb-3">Horário</h4><p class="text-dark-text/50 dark:text-neutral-500 text-sm">Segunda a Sábado<br/>17:30 às 22:30</p></div>
                   </div>
                </div>
              </div>
              <div class="w-full lg:w-1/2 h-[600px] relative reveal-on-scroll shadow-[0_20px_50px_rgba(0,0,0,0.1)] rounded-3xl overflow-hidden border border-black/5 dark:border-white/5 group">
                <iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3686.299658249692!2d-46.96691642382121!3d-22.42566487401147!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x94c8f9006208546b%3A0xf1877d21099b3bd1!2sMogi%20Campe%C3%A3o%20do%20Churrasco%20-%2022%20de%20Outubro!5e0!3m2!1spt-BR!2sbr!4v1739316684000!5m2!1spt-BR!2sbr" width="100%" height="100%" style="border:0; filter: grayscale(0.2) contrast(1.1) invert(var(--map-invert, 0))" allowfullscreen="" loading="lazy"></iframe>
              </div>
            </div>
          </div>
        </section>

        <!-- FOOTER -->
        <footer class="bg-white dark:bg-neutral-900 border-t border-black/5 dark:border-white/5 py-16 md:py-24 px-6 relative overflow-hidden transition-colors duration-300">
           <div class="container mx-auto relative z-10 flex flex-col md:flex-row justify-between items-center gap-10 md:gap-16">
              <div class="flex flex-col md:flex-row items-center gap-6 text-center md:text-left">
                 {render_logo(size="md", classes="md:w-32 md:h-32 shadow-brand-blue/10 shadow-2xl")}
                 <div>
                    <span class="font-bebas text-3xl md:text-4xl tracking-widest text-dark-text dark:text-neutral-100 uppercase">Campeão do Churrasco</span>
                    <span class="block text-[10px] md:text-[12px] text-brand-blue tracking-[0.3em] font-bold uppercase mt-2">O sabor da tradição</span>
                 </div>
              </div>
              <div class="text-center md:text-right">
                 <p class="text-dark-text dark:text-neutral-300 text-sm md:text-base font-bold uppercase tracking-[0.4em] mb-4">Aberto todos os dias</p>
                 <p class="text-dark-text/40 dark:text-neutral-500 text-xs font-medium tracking-wider">Av. 22 de Outubro, 630 • Mogi Mirim<br/>© 2026</p>
              </div>
           </div>
           <div class="absolute -bottom-10 left-1/2 -translate-x-1/2 font-bebas text-[15vw] text-black/[0.03] dark:text-white/[0.02] pointer-events-none whitespace-nowrap">CAMPEÃO DO CHURRASCO</div>
        </footer>

        <!-- JS LOGIC -->
        <script>
            // DARK MODE LOGIC
            function toggleDarkMode() {{
                const html = document.documentElement;
                const dot = document.getElementById('theme-toggle-dot');
                
                if (html.classList.contains('dark')) {{
                    html.classList.remove('dark');
                    localStorage.setItem('theme', 'light');
                    document.body.style.setProperty('--map-invert', '0');
                }} else {{
                    html.classList.add('dark');
                    localStorage.setItem('theme', 'dark');
                    document.body.style.setProperty('--map-invert', '0.9');
                }}
            }}

            // ADMIN LOGIC
            const ADMIN_TOKEN = "admin_logged_in";
            
            function showAdminLogin() {{
                document.getElementById('admin-modal').classList.remove('hidden');
                document.getElementById('admin-password').focus();
            }}

            function closeAdminModal() {{
                document.getElementById('admin-modal').classList.add('hidden');
                document.getElementById('admin-password').value = '';
            }}

            function attemptAdminLogin() {{
                const pwd = document.getElementById('admin-password').value;
                if (pwd === "230923") {{ // Updated access code
                    localStorage.setItem(ADMIN_TOKEN, "true");
                    updateAdminUI();
                    closeAdminModal();
                    alert("Acesso Administrativo Ativado!");
                }} else {{
                    alert("Código incorreto!");
                }}
            }}

            function logoutAdmin() {{
                localStorage.removeItem(ADMIN_TOKEN);
                location.reload();
            }}

            function updateAdminUI() {{
                const isAdmin = localStorage.getItem(ADMIN_TOKEN) === "true";
                if (isAdmin) {{
                    document.getElementById('admin-login-section').classList.add('hidden');
                    document.getElementById('admin-active-section').classList.remove('hidden');
                    document.querySelectorAll('.admin-only').forEach(el => el.classList.remove('hidden'));
                }}
            }}

            async function toggleAvailability(productId) {{
                try {{
                    const response = await fetch(`/admin/toggle/${{productId}}`, {{ method: 'POST' }});
                    const data = await response.json();
                    
                    if (data.status === 'success') {{
                        const card = document.getElementById(`product-card-${{productId}}`);
                        const badge = document.getElementById(`status-badge-${{productId}}`);
                        
                        if (data.is_available) {{
                            card.classList.remove('opacity-50', 'grayscale', 'select-none');
                            badge.classList.add('hidden');
                        }} else {{
                            card.classList.add('opacity-50', 'grayscale', 'select-none');
                            badge.classList.remove('hidden');
                        }}
                    }}
                }} catch (error) {{
                    console.error("Error toggling availability:", error);
                }}
            }}

            // TABS LOGIC
            function switchTab(catId) {{
                // Hide all contents
                document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
                document.querySelectorAll('.tab-btn').forEach(el => {{
                    el.classList.remove('bg-brand-blue', 'text-white', 'shadow-[0_5px_15px_rgba(0,144,255,0.2)]');
                    el.classList.add('text-dark-text/40');
                    el.classList.add('hover:bg-brand-blue/10', 'hover:text-brand-blue');
                }});
                
                // Show target
                document.getElementById('tab-content-' + catId).classList.add('active');
                
                // Highlight button
                const btn = document.getElementById('tab-btn-' + catId);
                btn.classList.remove('text-dark-text/40', 'hover:bg-brand-blue/10', 'hover:text-brand-blue');
                btn.classList.add('bg-brand-blue', 'text-white', 'shadow-[0_5px_15px_rgba(0,144,255,0.2)]');

                // Reset sub-filters when switching tabs
                filterSubCat('all');
            }}

            // SUB-CATEGORY FILTERING
            function filterSubCat(subCat) {{
                // Update buttons
                document.querySelectorAll('.subcat-btn').forEach(btn => {{
                    if (btn.innerText.toLowerCase() === subCat.toLowerCase() || (subCat === 'all' && btn.innerText === 'Todos')) {{
                        btn.classList.add('bg-brand-blue', 'text-white');
                        btn.classList.remove('text-dark-text/60', 'dark:text-neutral-400');
                    }} else {{
                        btn.classList.remove('bg-brand-blue', 'text-white');
                        btn.classList.add('text-dark-text/60', 'dark:text-neutral-400');
                    }}
                }});

                // Filter cards
                document.querySelectorAll('.product-card').forEach(card => {{
                    const cardSubCat = card.getAttribute('data-subcat');
                    if (subCat === 'all' || cardSubCat === subCat) {{
                        card.style.display = 'flex';
                    }} else {{
                        card.style.display = 'none';
                    }}
                }});
                
                // Refresh ScrollTrigger as heights change
                ScrollTrigger.refresh();
            }}

            // GSAP ANIMATIONS
            document.addEventListener("DOMContentLoaded", (event) => {{
                gsap.registerPlugin(ScrollTrigger);

                // Reveal on scroll
                gsap.utils.toArray('.reveal-on-scroll').forEach(section => {{
                    gsap.fromTo(section, 
                        {{ y: 50, opacity: 0 }},
                        {{ y: 0, opacity: 1, duration: 1, ease: 'power3.out',
                           scrollTrigger: {{ trigger: section, start: 'top 85%' }}
                        }}
                    );
                }});

                // Hero Title Split
                const heroTitle = document.querySelector('#hero-title');
                // (Simplified animation for vanilla JS)
                gsap.fromTo(heroTitle, {{ y: 50, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 1, ease: 'power4.out' }});

                gsap.fromTo('#hero-subtitle', {{ y: 20, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 1, delay: 0.2 }});
                gsap.fromTo('#hero-indicator', {{ opacity: 0 }}, {{ opacity: 1, duration: 1.5, delay: 0.5 }});
                
                // Set map initial state
                if (document.documentElement.classList.contains('dark')) {{
                    document.body.style.setProperty('--map-invert', '0.9');
                }}
                
                // Initial Admin Check
                updateAdminUI();
            }});
        </script>
    </body>
    </html>
    """

import re
import os
from django.conf import settings
from django.shortcuts import redirect


class PasswordChangeRequiredMiddleware:
	"""Middleware que fuerza el cambio de contraseña si el usuario tiene una clave provisoria.
	
	Si el usuario está autenticado y tiene el flag debe_cambiar_clave=True,
	redirige a la vista de cambio de contraseña obligatorio.
	
	Exclusiones:
	  - Rutas de autenticación (login, logout, cambiar contraseña)
	  - Rutas estáticas y admin
	"""
	
	def __init__(self, get_response):
		self.get_response = get_response
		self.change_password_url = '/autenticacion/cambiar_password/'
		
		self._exempt_patterns = [
			re.compile(r'^static/.*'),
			re.compile(r'^media/.*'),
			re.compile(r'^admin/.*'),
			re.compile(r'^autenticacion/login/?$'),
			re.compile(r'^autenticacion/logout/?$'),
			re.compile(r'^autenticacion/cambiar_password/?$'),
		]
	
	def __call__(self, request):
		# Solo aplicar si el usuario está autenticado
		if not request.user.is_authenticated:
			return self.get_response(request)
		
		path = request.path.lstrip('/')
		
		# Verificar si la ruta está exenta
		for pattern in self._exempt_patterns:
			if pattern.match(path):
				return self.get_response(request)
		
		# Verificar si el usuario tiene un perfil y debe cambiar la clave
		try:
			perfil = request.user.perfil
			if perfil.debe_cambiar_clave:
				# Si ya está en la página de cambio de contraseña, permitir acceso
				if path.startswith(self.change_password_url.lstrip('/')):
					return self.get_response(request)
				# Redirigir a cambio de contraseña
				return redirect(self.change_password_url)
		except Exception:
			# Si no tiene perfil o hay algún error, continuar normalmente
			pass
		
		return self.get_response(request)


class LoginRequiredMiddleware:
	"""Middleware que exige autenticación para acceder al sitio.

	Exclusiones (no obligan login):
	  - Rutas estáticas: /static/, /media/
	  - Admin y su login: /admin/*
	  - Autenticación: /autenticacion/login, /autenticacion/logout, recuperación (prefijo)
	  - Rutas de prueba de errores: /ver-404, /forzar-404
	  - Cualquier patrón agregado en settings.LOGIN_EXEMPT_URLS (lista de regex)

	Desactivación rápida: exporta DJANGO_DISABLE_LOGIN_MIDDLEWARE=True

	Si el usuario no está autenticado y la ruta no está exenta, redirige a LOGIN_URL
	agregando ?next=<ruta> para volver tras login.
	"""

	def __init__(self, get_response):
		self.get_response = get_response
		self.login_url = settings.LOGIN_URL or '/autenticacion/login/'

		custom_exempt = getattr(settings, 'LOGIN_EXEMPT_URLS', []) or []
		self._patterns = [re.compile(p) for p in custom_exempt]

		default_patterns = [
			r'^static/.*',
			r'^media/.*',
			r'^admin/.*',
			r'^autenticacion/login/?$',
			r'^autenticacion/logout/?$',
			r'^autenticacion/recuperar.*',
			r'^ver-404/?$',
			r'^forzar-404/?$',
		]
		self._patterns.extend(re.compile(p) for p in default_patterns)

	def __call__(self, request):
		# Permitir desactivar por variable de entorno sin tocar settings
		if os.getenv('DJANGO_DISABLE_LOGIN_MIDDLEWARE') == 'True':
			return self.get_response(request)

		# Ya autenticado -> continuar
		if request.user.is_authenticated:
			return self.get_response(request)

		path = request.path.lstrip('/')  # normalizamos para coincidencias regex

		for pattern in self._patterns:
			if pattern.match(path):
				return self.get_response(request)

		# Evita loop si ya estamos en la página de login
		if path.startswith(self.login_url.lstrip('/')):
			return self.get_response(request)

		# Redirige a login con parámetro next
		return redirect(f"{self.login_url}?next={request.path}")


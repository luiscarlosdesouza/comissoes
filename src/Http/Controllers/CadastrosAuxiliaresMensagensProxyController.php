<?php

namespace Uspdev\UspTheme\Http\Controllers;

use Illuminate\Http\JsonResponse;
use Uspdev\UspTheme\Services\CadastrosAuxiliaresMensagensService;

class CadastrosAuxiliaresMensagensProxyController
{
    public function __invoke(CadastrosAuxiliaresMensagensService $service): JsonResponse
    {
        $enabled = filter_var(
            config('laravel-usp-theme.cadastros_auxiliares_mensagens_integracao', false),
            FILTER_VALIDATE_BOOL,
            FILTER_NULL_ON_FAILURE
        ) ?? false;

        if (!$enabled) {
            return response()->json([]);
        }

        $isAuth = auth()->guard('web')->check();

        $mensagens = $service->fetch()
            ->filter(function ($mensagem) use ($isAuth) {
                return $this->deveExibirMensagem($mensagem, $isAuth);
            })
            ->values();

        return response()->json($mensagens);
    }

    private function deveExibirMensagem(mixed $mensagem, bool $isAuth): bool
    {
        if (!is_array($mensagem)) {
            return false;
        }

        if (($mensagem['ativo'] ?? true) === false) {
            return false;
        }

        $publico = $mensagem['publico'] ?? null;

        if (is_bool($publico)) {
            return $publico ? true : $isAuth;
        }

        if (is_array($publico)) {
            $publicosNormalizados = collect($publico)
                ->map(function ($item) {
                    return $this->normalizarPublico($item);
                })
                ->filter()
                ->values();

            if ($publicosNormalizados->contains('usuario')) {
                return $isAuth;
            }
        }

        if (is_string($publico) && trim($publico) !== '') {
            $publicosNormalizados = collect(explode(',', $publico))
                ->map(function ($item) {
                    return $this->normalizarPublico($item);
                })
                ->filter()
                ->values();

            if ($publicosNormalizados->contains('usuario')) {
                return $isAuth;
            }
        }

        return true;
    }

    private function normalizarPublico(mixed $item): string
    {
        $texto = mb_strtolower(trim((string) $item));

        return str_replace('á', 'a', $texto);
    }
}

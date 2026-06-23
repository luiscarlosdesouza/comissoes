<?php

namespace Uspdev\UspTheme\Services;

use Illuminate\Http\Request;
use Illuminate\Support\Collection;
use Uspdev\CadastrosAuxiliaresClient\Contracts\MensagensClientInterface;

class CadastrosAuxiliaresMensagensService
{
    public function __construct(private readonly MensagensClientInterface $client)
    {
    }

    public function fetch(): Collection
    {
        $enabled = filter_var(
            config('laravel-usp-theme.cadastros_auxiliares_mensagens_integracao', false),
            FILTER_VALIDATE_BOOL,
            FILTER_NULL_ON_FAILURE
        ) ?? false;
        $endpoint = trim((string) config('laravel-usp-theme.cadastros_auxiliares_mensagens_endpoint_url', ''));

        if (!$enabled || $endpoint === '' || app()->runningInConsole()) {
            return collect();
        }

        if (app()->bound('request')) {
            $request = app('request');

            if ($request->is('api/*') || $request->headers->get('X-UspTheme-Mensagens-Internal') === '1') {
                return collect();
            }
        }

        if ($this->shouldUseInternalRequest($endpoint)) {
            return $this->fetchViaInternalRequest($endpoint);
        }

        $limite = max(1, (int) config('laravel-usp-theme.cadastros_auxiliares_mensagens_limite', 5));
        $sistema = mb_strtolower(trim((string) config('laravel-usp-theme.cadastros_auxiliares_mensagens_sistema', '')));
        $password = trim((string) config('laravel-usp-theme.cadastros_auxiliares_password', ''));

        // Mantem compatibilidade: tema continua lendo CADASTROS_AUXILIARES_*.
        config()->set('cadastros-auxiliares-client.enabled', true);
        config()->set('cadastros-auxiliares-client.mensagens.endpoint_url', $endpoint);
        config()->set('cadastros-auxiliares-client.mensagens.password', $password);
        config()->set('cadastros-auxiliares-client.mensagens.limite', $limite);
        config()->set('cadastros-auxiliares-client.mensagens.sistema', $sistema);

        $filters = [
            'ativos' => true,
            'limite' => $limite,
        ];

        if ($sistema !== '') {
            $filters['sistema'] = $sistema;
        }

        return $this->client->fetch($filters)->values();
    }

    private function shouldUseInternalRequest(string $url): bool
    {
        if (!app()->bound('request')) {
            return false;
        }

        $endpointHost = parse_url($url, PHP_URL_HOST);
        $currentHost = app('request')->getHost();

        return !empty($endpointHost) && $endpointHost === $currentHost;
    }

    private function fetchViaInternalRequest(string $url): Collection
    {
        $path = parse_url($url, PHP_URL_PATH) ?: '/api/mensagens';
        $query = parse_url($url, PHP_URL_QUERY) ?: '';
        $uri = $path . ($query ? ('?' . $query) : '');

        $internalRequest = Request::create($uri, 'GET', [], [], [], [
            'HTTP_X_UspTheme_Mensagens_Internal' => '1',
        ]);

        $response = app()->handle($internalRequest);

        if ($response->getStatusCode() !== 200) {
            return collect();
        }

        $payload = json_decode($response->getContent(), true);

        return is_array($payload) ? collect($payload)->values() : collect();
    }
}

<?php
/**
 * Plugin Name: IME USP Comissões Shortcode
 * Description: Disponibiliza o shortcode [comissoes_ime] para listar os colegiados consumindo a API Python.
 * Version: 1.1
 * Author: IME USP
 */

if (!defined('ABSPATH')) {
    exit; // Segurança para evitar acesso direto
}

/**
 * Função principal do shortcode [comissoes_ime]
 */
function ime_comissoes_shortcode_render($atts) {
    // Configura a URL da API FastAPI (Mude caso a API não esteja no mesmo servidor do WP)
    // O endpoint /html já retorna o layout limpo, com accordion e CSS isolado (classes ime-)
    $api_url = 'http://localhost:8020/api/comissoes/html';

    // Tenta buscar usando a API nativa do WordPress
    $response = wp_remote_get($api_url, array(
        'timeout'     => 15, // Tempo razoável de espera
        'sslverify'   => false
    ));

    // Tratamento de erro de conexão
    if (is_wp_error($response)) {
        return '<div class="ime-comissao-container"><p style="color:red;">Erro ao conectar com a API de Comissões: ' . esc_html($response->get_error_message()) . '</p></div>';
    }

    $response_code = wp_remote_retrieve_response_code($response);
    
    // Tratamento de erro HTTP
    if ($response_code !== 200) {
        return '<div class="ime-comissao-container"><p style="color:red;">O serviço de comissões está temporariamente indisponível (Erro ' . esc_html($response_code) . ').</p></div>';
    }

    // Pega o corpo da resposta, que é o HTML já formatado com o accordion
    $html_body = wp_remote_retrieve_body($response);

    // DICA: O "carregamento quando o usuário clica" (Accordion) e a ausência de conflitos
    // com o tema atual já são garantidos pelo template gerado lá no FastAPI (com as classes ime-).
    // Dessa forma, se você trocar de tema no WordPress, o layout não quebra.

    return $html_body;
}

// Registra o shortcode
add_shortcode('comissoes_ime', 'ime_comissoes_shortcode_render');

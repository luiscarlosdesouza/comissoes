<?php
/*
Plugin Name: IME USP Comissões Shortcode
Description: Adiciona o shortcode [ime_comissoes] que busca as comissões da API Python (FastAPI) e renderiza na página.
Version: 1.0
Author: IME USP
*/

if (!defined('ABSPATH')) {
    exit; // Segurança
}

function ime_comissoes_shortcode($atts) {
    $a = shortcode_atts(array(
        'id'     => '',
        'ids'    => '',
        'tipo'   => '',
        'layout' => 'acordeon'
    ), $atts);

    $api_url = 'http://localhost:8020/api/comissoes/html';
    $query_args = array();

    if (!empty($a['id'])) {
        $id = sanitize_text_field($a['id']);
        $api_url = "http://localhost:8020/api/comissao/{$id}/html";
    } else {
        if (!empty($a['ids'])) {
            $query_args['ids'] = sanitize_text_field($a['ids']);
        }
        if (!empty($a['tipo'])) {
            $query_args['tipo'] = sanitize_text_field($a['tipo']);
        }
    }

    if (!empty($a['layout'])) {
        $query_args['layout'] = sanitize_text_field($a['layout']);
    }

    if (!empty($query_args)) {
        $api_url = add_query_arg($query_args, $api_url);
    }

    // Faz a requisição HTTP para a API
    $response = wp_remote_get($api_url, array(
        'timeout' => 15,
        'sslverify' => false
    ));

    if (is_wp_error($response)) {
        return '<p>Erro ao carregar as comissões. ' . esc_html($response->get_error_message()) . '</p>';
    }

    $response_code = wp_remote_retrieve_response_code($response);
    
    if ($response_code !== 200) {
        return '<p>O serviço de comissões está temporariamente indisponível (Erro ' . esc_html($response_code) . ').</p>';
    }

    $html_body = wp_remote_retrieve_body($response);

    // Retorna o HTML que será renderizado no local do shortcode
    return $html_body;
}

add_shortcode('ime_comissoes', 'ime_comissoes_shortcode');

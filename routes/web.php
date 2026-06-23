<?php

use Illuminate\Support\Facades\Route;
use Uspdev\UspTheme\Http\Controllers\CadastrosAuxiliaresMensagensProxyController;

Route::middleware('web')->group(function () {
    Route::get('/_usp-theme/cadastros-auxiliares/mensagens', CadastrosAuxiliaresMensagensProxyController::class)
        ->name('usp-theme.cadastros-auxiliares.mensagens-proxy');
});

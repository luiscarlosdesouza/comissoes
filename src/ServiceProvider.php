<?php

namespace Uspdev\UspTheme;

use Illuminate\Contracts\Config\Repository;
use Illuminate\Contracts\Events\Dispatcher;
use Illuminate\Contracts\View\Factory;
use Illuminate\Support\Facades\View;
use Illuminate\Support\ServiceProvider as BaseServiceProvider;
use Uspdev\CadastrosAuxiliaresClient\Contracts\MensagensClientInterface;
use Uspdev\CadastrosAuxiliaresClient\Services\MensagensClient;
use Uspdev\UspTheme\Services\CadastrosAuxiliaresMensagensService;

class ServiceProvider extends BaseServiceProvider
{
    /**
     * Bootstrap services.
     *
     * @return void
     */
    public function boot(Factory $view, Dispatcher $events, Repository $config)
    {
        $this->loadViews();
        $this->loadTranslations();
        $this->loadRoutes();
        $this->publishAssets();
        $this->publishConfig();

        // config
        View::share('title', config('laravel-usp-theme.title'));
        View::share('container', config('laravel-usp-theme.container') ?? 'container-fluid');
        View::share('menu', config('laravel-usp-theme.menu'));
        View::share('right_menu', config('laravel-usp-theme.right_menu'));
        View::share('app_url', config('laravel-usp-theme.app_url'));
        View::share('logout_method', config('laravel-usp-theme.logout_method'));
        View::share('login_url', config('laravel-usp-theme.login_url'));
        View::share('logout_url', config('laravel-usp-theme.logout_url'));

        # skin na sessão com fallback para o config
        # https://stackoverflow.com/questions/34577946/how-to-retrieve-session-data-in-service-providers-in-laravel
        view()->composer('*', function ($view) {
            $view->with('skin', session(config('laravel-usp-theme.session_key') . '.skin') ?? config('laravel-usp-theme.skin'));
        });

    }

    /**
     * Register services.
     *
     * @return void
     */
    public function register()
    {
        // configs
        $this->mergeConfigFrom($this->packagePath('config/laravel-usp-theme.php'), 'laravel-usp-theme');
        $this->mergeConfigFrom($this->packagePath('config/skins.php'), 'laravel-usp-theme');
        $sistemas = require $this->packagePath('config/laravel-usp-theme-sistemas.php');
        $config = $this->app['config']->get('laravel-usp-theme', []);
        $this->app['config']->set('laravel-usp-theme', array_merge($sistemas, $config));

        // Fallback binding for environments where package:discover has not been executed yet.
        if (
            interface_exists(MensagensClientInterface::class)
            && class_exists(MensagensClient::class)
            && !$this->app->bound(MensagensClientInterface::class)
        ) {
            $this->app->singleton(MensagensClientInterface::class, MensagensClient::class);
        }

        $this->app->singleton(CadastrosAuxiliaresMensagensService::class);

        // Facade
        $this->app->bind('uspTheme', UspTheme::class);
    }

    private function packagePath($path)
    {
        return __DIR__ . "/../$path";
    }

    private function loadViews()
    {
        $viewsPath = $this->packagePath('resources/views');
        $this->loadViewsFrom($viewsPath, 'laravel-usp-theme');
        $this->publishes([
            $viewsPath => base_path('resources/views/vendor/laravel-usp-theme'),
        ], 'views');
    }

    private function loadTranslations()
    {
        $translationsPath = $this->packagePath('resources/lang');
        $this->loadTranslationsFrom($translationsPath, 'laravel-usp-theme');
        $this->publishes([
            $translationsPath => base_path('resources/lang/vendor/laravel-usp-theme'),
        ], 'translations');
    }

    private function publishAssets()
    {
        $this->publishes([
            $this->packagePath('resources/assets') => public_path('vendor/laravel-usp-theme'),
        ], 'assets');
    }

    private function loadRoutes()
    {
        $this->loadRoutesFrom($this->packagePath('routes/web.php'));
    }

    private function publishConfig()
    {
        $configPath = $this->packagePath('config/laravel-usp-theme.php');
        $this->publishes([
            $configPath => config_path('laravel-usp-theme.php'),
        ], 'config');
    }

}

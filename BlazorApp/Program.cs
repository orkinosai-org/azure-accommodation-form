using BlazorApp.Components;
using BlazorApp.Data;
using BlazorApp.Services;
using Microsoft.EntityFrameworkCore;

namespace BlazorApp;

public class Program
{
    public static void Main(string[] args)
    {
        Console.WriteLine("--------- PROGRAM MAIN HIT ---------");

        var builder = WebApplication.CreateBuilder(args);

        // Configure logging to disable Azure diagnostics dependencies
        builder.Logging.ClearProviders();
        builder.Logging.AddConsole();
        builder.Logging.AddDebug();
        
        // Disable Azure App Service diagnostics trace listeners that require DIAGNOSTICS_AZUREBLOBCONTAINERSASURL
        // This prevents startup failures when Azure App Service diagnostics are enabled but not properly configured
        builder.Logging.AddFilter("Microsoft.Extensions.Logging.AzureAppServices.Internal.AzureBlobLoggerProvider", LogLevel.None);
        builder.Logging.AddFilter("Microsoft.Extensions.Logging.AzureAppServices", LogLevel.None);

        // Add services to the container.
        builder.Services.AddRazorComponents()
            .AddInteractiveServerComponents()
            .AddInteractiveWebAssemblyComponents();

        // Add Entity Framework
        builder.Services.AddDbContext<ApplicationDbContext>(options =>
        {
            if (builder.Environment.IsDevelopment())
            {
                options.UseSqlite(builder.Configuration.GetConnectionString("DefaultConnection"));
            }
            else
            {
                options.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection"));
            }
        });

        // Add API controllers
        builder.Services.AddControllers();
        
        // Add MVC services
        builder.Services.AddControllersWithViews();

        // Configure settings
        builder.Services.Configure<EmailSettings>(
            builder.Configuration.GetSection("EmailSettings"));
        builder.Services.Configure<BlobStorageSettings>(
            builder.Configuration.GetSection("BlobStorageSettings"));
        builder.Services.Configure<ApplicationSettings>(
            builder.Configuration.GetSection("ApplicationSettings"));

        // Register services
        builder.Services.AddScoped<IFormService, FormService>();
        builder.Services.AddScoped<IEmailService, EmailService>();
        builder.Services.AddScoped<IPdfGenerationService, PdfGenerationService>();
        builder.Services.AddScoped<IBlobStorageService, BlobStorageService>();
        builder.Services.AddScoped<IDebugConsoleHelper, DebugConsoleHelper>();

        // Register HTTP client for API calls
        builder.Services.AddHttpClient<IFormApiService, FormApiService>(client =>
        {
            var baseAddress = builder.Configuration["ApplicationSettings:ApplicationUrl"] ?? "https://localhost:5001";
            client.BaseAddress = new Uri(baseAddress);
        });

        // Add CORS for API endpoints
        builder.Services.AddCors(options =>
        {
            options.AddDefaultPolicy(policy =>
            {
                policy.AllowAnyOrigin()
                      .AllowAnyMethod()
                      .AllowAnyHeader();
            });
        });

        // Add API documentation
        builder.Services.AddEndpointsApiExplorer();
        builder.Services.AddSwaggerGen();

        var app = builder.Build();

        // Configure the HTTP request pipeline.
        if (!app.Environment.IsDevelopment())
        {
            app.UseExceptionHandler("/Error");
            // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
            app.UseHsts();
        }
        else
        {
            app.UseSwagger();
            app.UseSwaggerUI();
            app.UseWebAssemblyDebugging();
        }

        app.UseHttpsRedirection();
        app.UseStaticFiles();
        
        // Serve WASM static files
        app.UseBlazorFrameworkFiles();
        
        app.UseRouting();

        app.UseCors();
        app.UseAntiforgery();

        // Map MVC controllers with default route (highest priority)
        app.MapControllerRoute(
            name: "default",
            pattern: "{controller=Home}/{action=Index}/{id?}");
            
        // Map API controllers
        app.MapControllers();
        
        // Map Server-side Blazor Components for specific routes
        app.MapRazorComponents<ServerApp>()
            .AddInteractiveServerRenderMode();
        
        // Map WASM fallback for all other unmatched requests (lowest priority)
        app.MapFallbackToFile("index.html");

        // Ensure database is created
        using (var scope = app.Services.CreateScope())
        {
            var context = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
            context.Database.EnsureCreated();
        }

        app.Run();
    }
}

namespace BlazorApp.Services;

public class EmailSettings
{
    public string SmtpServer { get; set; } = string.Empty;
    public int SmtpPort { get; set; } = 587;
    public string SmtpUsername { get; set; } = string.Empty;
    public string SmtpPassword { get; set; } = string.Empty;
    public bool UseSsl { get; set; } = true;
    public string FromEmail { get; set; } = string.Empty;
    public string FromName { get; set; } = string.Empty;
    public string CompanyEmail { get; set; } = string.Empty;
}

public class BlobStorageSettings
{
    public string ConnectionString { get; set; } = string.Empty;
    public string ContainerName { get; set; } = "form-submissions";
}

public class ApplicationSettings
{
    public string ApplicationName { get; set; } = "Azure Accommodation Form";
    public string ApplicationUrl { get; set; } = string.Empty;
    public int TokenExpirationMinutes { get; set; } = 15;
    public int TokenLength { get; set; } = 6;
}
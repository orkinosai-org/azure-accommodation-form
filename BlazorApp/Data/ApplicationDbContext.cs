using Microsoft.EntityFrameworkCore;
using BlazorApp.Models;

namespace BlazorApp.Data;

public class ApplicationDbContext : DbContext
{
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
        : base(options)
    {
    }

    public DbSet<FormSubmissionEntity> FormSubmissions { get; set; }
    public DbSet<FormSubmissionLog> FormSubmissionLogs { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Configure FormSubmissionEntity
        modelBuilder.Entity<FormSubmissionEntity>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => e.SubmissionId).IsUnique();
            entity.HasIndex(e => e.UserEmail);
            entity.HasIndex(e => e.SubmittedAt);
            entity.HasIndex(e => e.Status);
            
            entity.Property(e => e.SubmissionId)
                .HasMaxLength(50)
                .IsRequired();
                
            entity.Property(e => e.FormDataJson)
                .IsRequired();
                
            entity.Property(e => e.UserEmail)
                .HasMaxLength(320);
                
            entity.Property(e => e.PdfFileName)
                .HasMaxLength(500);
                
            entity.Property(e => e.BlobStorageUrl)
                .HasMaxLength(2000);
                
            entity.Property(e => e.ClientIpAddress)
                .HasMaxLength(50);
                
            // Enhanced metadata fields
            entity.Property(e => e.UserAgent)
                .HasMaxLength(1000);
                
            entity.Property(e => e.Referrer)
                .HasMaxLength(2000);
                
            entity.Property(e => e.AcceptLanguage)
                .HasMaxLength(200);
                
            entity.Property(e => e.Origin)
                .HasMaxLength(2000);
                
            entity.Property(e => e.XForwardedFor)
                .HasMaxLength(500);
                
            entity.Property(e => e.XRealIp)
                .HasMaxLength(50);
                
            entity.Property(e => e.ContentType)
                .HasMaxLength(200);
                
            entity.Property(e => e.RequestMetadataJson)
                .HasMaxLength(4000);
                
            entity.Property(e => e.EmailVerificationToken)
                .HasMaxLength(10);
        });

        // Configure FormSubmissionLog
        modelBuilder.Entity<FormSubmissionLog>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => e.FormSubmissionId);
            entity.HasIndex(e => e.Timestamp);
            
            entity.Property(e => e.Action)
                .HasMaxLength(100)
                .IsRequired();
                
            entity.Property(e => e.Details)
                .HasMaxLength(2000);

            // Configure relationship
            entity.HasOne(e => e.FormSubmission)
                .WithMany(e => e.Logs)
                .HasForeignKey(e => e.FormSubmissionId)
                .OnDelete(DeleteBehavior.Cascade);
        });
    }
}
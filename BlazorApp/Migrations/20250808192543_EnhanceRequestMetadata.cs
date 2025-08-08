using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace BlazorApp.Migrations
{
    /// <inheritdoc />
    public partial class EnhanceRequestMetadata : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "AcceptLanguage",
                table: "FormSubmissions",
                type: "TEXT",
                maxLength: 200,
                nullable: true);

            migrationBuilder.AddColumn<long>(
                name: "ContentLength",
                table: "FormSubmissions",
                type: "INTEGER",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "ContentType",
                table: "FormSubmissions",
                type: "TEXT",
                maxLength: 200,
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "Origin",
                table: "FormSubmissions",
                type: "TEXT",
                maxLength: 2000,
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "Referrer",
                table: "FormSubmissions",
                type: "TEXT",
                maxLength: 2000,
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "RequestMetadataJson",
                table: "FormSubmissions",
                type: "TEXT",
                maxLength: 4000,
                nullable: false,
                defaultValue: "");

            migrationBuilder.AddColumn<string>(
                name: "UserAgent",
                table: "FormSubmissions",
                type: "TEXT",
                maxLength: 1000,
                nullable: false,
                defaultValue: "");

            migrationBuilder.AddColumn<string>(
                name: "XForwardedFor",
                table: "FormSubmissions",
                type: "TEXT",
                maxLength: 500,
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "XRealIp",
                table: "FormSubmissions",
                type: "TEXT",
                maxLength: 50,
                nullable: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "AcceptLanguage",
                table: "FormSubmissions");

            migrationBuilder.DropColumn(
                name: "ContentLength",
                table: "FormSubmissions");

            migrationBuilder.DropColumn(
                name: "ContentType",
                table: "FormSubmissions");

            migrationBuilder.DropColumn(
                name: "Origin",
                table: "FormSubmissions");

            migrationBuilder.DropColumn(
                name: "Referrer",
                table: "FormSubmissions");

            migrationBuilder.DropColumn(
                name: "RequestMetadataJson",
                table: "FormSubmissions");

            migrationBuilder.DropColumn(
                name: "UserAgent",
                table: "FormSubmissions");

            migrationBuilder.DropColumn(
                name: "XForwardedFor",
                table: "FormSubmissions");

            migrationBuilder.DropColumn(
                name: "XRealIp",
                table: "FormSubmissions");
        }
    }
}

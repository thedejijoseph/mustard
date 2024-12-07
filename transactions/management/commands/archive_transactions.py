import datetime
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from transactions.models import Transaction, TransactionArchive

class Command(BaseCommand):
    help = "Archive transactions older than a specified number of months"

    def add_arguments(self, parser):
        parser.add_argument(
            '--months', 
            type=int, 
            default=3, 
            help="Specify the age of transactions to archive in months (default: 3 months)"
        )

    def handle(self, *args, **options):
        months = options['months']
        cutoff_date = now() - datetime.timedelta(days=months * 30)

        self.stdout.write(
            f"Archiving transactions older than {months} month(s) (cutoff date: {cutoff_date.date()})..."
        )

        # Fetch transactions older than the cutoff date
        transactions_to_archive = Transaction.objects.filter(created_at__lt=cutoff_date)

        if not transactions_to_archive.exists():
            self.stdout.write("No transactions to archive.")
            return

        # Archive transactions
        archived_count = 0
        for transaction in transactions_to_archive:
            TransactionArchive.objects.update_or_create(
                transaction_id=transaction.transaction_id,
                defaults={
                    "masked_pan": transaction.masked_pan,
                    "encrypted_pan": transaction.encrypted_pan,
                    "encrypted_expiry": transaction.encrypted_expiry,
                    "amount": transaction.amount,
                    "created_at": transaction.created_at,
                    "updated_at": transaction.updated_at,
                }
            )
            transaction.delete()
            archived_count += 1

        self.stdout.write(f"Archived {archived_count} transaction(s).")

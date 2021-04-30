# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = True` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.utils import timezone
import pytz
from django.db.models import CASCADE
from users.models import User
import subprocess
import fitz
import os
from django.core.files import File
import random, string
import sys

def get_sha1sum(file_path):
    # find out sha1sum
    command_result = subprocess.run(['sha1sum', f"{file_path}"], stdout=subprocess.PIPE)
    sum=command_result.stdout.decode('utf-8').split()[0]
    return sum

def get_filesize(file_path):
    # find out filesize
    
    # macOS if-then-else fix
    print(f'operating system recognized as {sys.platform}')
    if sys.platform == "darwin":
        # @ macOS
        print("runnig in macOS")
        file_size=7 # hardcoded to just make it work.
        # or something like this ( maybe works in macOS? )
        #command_result = subprocess.run(['stat', '-f%s',f"{file_path}"], stdout=subprocess.PIPE)
        #file_size=int(command_result.stdout.decode('utf-8'))    
    else:
        # default (linux)
        command_result = subprocess.run(['stat', '--printf=%s',f"{file_path}"], stdout=subprocess.PIPE)
        file_size=int(command_result.stdout.decode('utf-8'))
    
    return file_size

def get_pagecount(file_path):
    # find out pagecount
    pagecount=fitz.open(f'{file_path}').pageCount
    return pagecount

class Pdf(models.Model):

    filex = models.FileField(upload_to="pdf", max_length=1000)
    filename = models.CharField(max_length=1000)
    size = models.IntegerField()
    sha1sum = models.CharField(max_length=40, unique=True)
    pagecount = models.IntegerField()
    created = models.DateTimeField(default=timezone.now)

    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)

    class Meta:
        managed = True
        db_table = 'doc_pdf'

    def save(self, *args, **kwargs):
        if self.pk is not None:
            # file already existed.
            super(Pdf, self).save(*args, **kwargs)
        else:
            # new file upload.
            
            try:
                # .user is set in view
                current_user_id=self.user.id
            except:
                current_user_id=1 # can be used in test which have no view

            # generate temp dummy values and save so we get access to file..
            dummy_sha1sum = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 35))    
            dummy_sha1sum = 'temp_' + dummy_sha1sum
            self.sha1sum = dummy_sha1sum
            self.size = 99
            self.pagecount = 99
            self.filename = 'temp'
            self.filex.name = os.path.basename(str(self.filex))
            super(Pdf, self).save(*args, **kwargs)
            
            sha1sum = get_sha1sum(f'media/{self.filex}')

            # check if the same document is already uploaded
            if Pdf.objects.filter(sha1sum=sha1sum).first() is None:
                # file does not already exist.

                # get correct values
                filename = os.path.basename(str(self.filex))
                filesize = get_filesize(f'media/{self.filex}')
                pagecount = get_pagecount(f'media/{self.filex}')

                # set correct values to this instance
                self.filename = filename              
                self.sha1sum = sha1sum

                self.size = filesize
                self.pagecount = pagecount
                final_path = f'pdf/{self.sha1sum}/{os.path.basename(str(self.filex))}'
                
                # move to correct path
                # this exist_ok because path already exists in media/ ( which it shouldn't )
                os.makedirs(os.path.dirname(f'media/{final_path}'), exist_ok=True)
                os.rename(f'media/{self.filex.name}', f'media/{final_path}')

                # update database with correct values
                self.filex.name = final_path
                super(Pdf, self).save(update_fields=['filename', 'sha1sum', 'size', 'pagecount', 'filex'])

                DocumentOwner.objects.create(document=self, owner=User.objects.get(id=current_user_id))
            else:
                # oh no. file already existed.
                # delete dummy file and database row.
                if self.filex:
                    self.filex.delete()
                super(Pdf, self).delete(*args, **kwargs)
                existing_document = Pdf.objects.filter(sha1sum=sha1sum).first()
                existing_owner = DocumentOwner.objects.raw(f'SELECT * FROM doc_owner WHERE document_id = {existing_document.id} AND owner_id = {current_user_id}')
                if len(existing_owner) == 0:
                    # create doc_owner for already existing file.
                    DocumentOwner.objects.create(document=existing_document, owner=User.objects.get(id=current_user_id))

    def _str_(self):
        return self.title

    def delete(self, *args, **kwargs):
        try:
            # .user is set in view
            current_user_id=self.user.id
        except:
            current_user_id=1 # can be used in test which have no view

        downer = DocumentOwner.objects.raw(f'SELECT * FROM doc_owner WHERE document_id = {self.pk} AND owner_id = {current_user_id}')
        if 1 == len(list(downer)):
            downer[0].delete()

        downers = DocumentOwner.objects.raw(f'SELECT * FROM doc_owner WHERE document_id = {self.pk}')
        if 0 == len(list(downers)):
            # file and path must be deleted manually.        
            if self.filex:
                path = f'media/{os.path.dirname(str(self.filex))}'
                possible_txt_file_path = f'media/{str(self.filex)}.txt'
                self.filex.delete()
                # delete also possible .txt file
                if os.path.exists(possible_txt_file_path):
                    os.remove(possible_txt_file_path)
                # delete empty directory
                os.rmdir(path)
            super(Pdf, self).delete(*args, **kwargs)

    def task_imagemagick_status(self):        
        task = DocumentTask.objects.raw(f'select id, document_id, name, status, time from doc_task where document_id = {self.id} and name = "{DocumentTask.DocTaskName.IMAGEMAGICK}" order by time desc limit 1;')
        if len(task) == 0:
            returnValue = "N/A"
        else:
            returnValue = task[0].status
        return returnValue

    def task_tesseract_db_status(self):
        task = DocumentTask.objects.raw(f'select id, document_id, name, status, time from doc_task where document_id = {self.id} and name = "{DocumentTask.DocTaskName.TESSERACT_DB}" order by time desc limit 1;')
        if len(task) == 0:
            returnValue = "N/A"
        else:
            returnValue = task[0].status
        return returnValue

    def task_tesseract_ocr_status(self):
        task = DocumentTask.objects.raw(f'select id, document_id, name, status, time from doc_task where document_id = {self.id} and name = "{DocumentTask.DocTaskName.TESSERACT_OCR}" order by time desc limit 1;')
        if len(task) == 0:
            returnValue = "N/A"
        else:
            returnValue = task[0].status
        return returnValue

class DocumentOwner(models.Model):
    document = models.ForeignKey(Pdf, on_delete=CASCADE)
    owner = models.ForeignKey(User, on_delete=CASCADE)
    upload_date = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = True
        db_table = 'doc_owner'
        
        unique_together = (('document', 'owner'),)

class DocumentTask(models.Model):

    class DocTaskName(models.TextChoices):
            IMAGEMAGICK = 'ImageMagick'
            TESSERACT_OCR = 'Tesseract_OCR'
            TESSERACT_DB = 'Tesseract_DB'

    class DocTaskStatus(models.TextChoices):
            WAITING = 'Waiting'
            RUNNING = 'Running'
            FINISHED = 'Finished'

    document = models.ForeignKey(Pdf, on_delete=CASCADE)
    name = models.CharField(
        max_length = 32,
        choices = DocTaskName.choices
    )
    status = models.CharField(
        max_length = 32,
        choices = DocTaskStatus.choices
    )
    time = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = True
        db_table = 'doc_task'

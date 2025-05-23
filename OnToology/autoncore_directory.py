def directory_magic(directory_watch, file_path, event_type, raise_exp=False):
    """
    Process ontology files from directory monitoring
    :param directory_watch: DirectoryWatch object
    :param file_path: relative path to the ontology file
    :param event_type: type of event (created, modified, manual_scan)
    :param raise_exp: whether to raise exceptions
    :return:
    """
    global g
    global parent_folder
    global log_file_dir
    global logger
    
    from OnToology.models import DirectoryWatch, OUser, Repo, ORun, OTask
    from django.utils import timezone
    import shutil
    
    try:
        # Set up logging for this directory processing
        user_email = directory_watch.user.email
        prepare_logger(f"{user_email}-dir-{directory_watch.id}")
        
        dolog(f"Starting directory magic for {file_path} in {directory_watch.path}")
        
        # Create a virtual repo entry for this directory
        virtual_repo_url = f"directory://{directory_watch.path}"
        
        # Get or create repo entry
        try:
            repo = Repo.objects.get(url=virtual_repo_url)
        except Repo.DoesNotExist:
            repo = Repo.objects.create(
                url=virtual_repo_url,
                state='Ready',
                notes=f'Directory watch for {directory_watch.path}'
            )
        
        # Create run entry
        orun = ORun.objects.create(
            user=directory_watch.user,
            repo=repo,
            branch='main'  # Default branch for directory processing
        )
        
        # Create initial task
        otask = OTask.objects.create(
            name='Directory Processing',
            description=f'Processing {file_path} ({event_type})',
            orun=orun,
            finished=False,
            success=False
        )
        
        # Update repo state
        repo.state = 'Processing'
        repo.save()
        
        # Set up working directory
        sec = ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(9)])
        work_dir = os.path.join(home, f'dir-work-{sec}')
        parent_folder = f'dir-work-{sec}'
        
        try:
            # Create working directory structure
            os.makedirs(work_dir, exist_ok=True)
            
            # Copy the ontology file to working directory
            source_file = os.path.join(directory_watch.path, file_path)
            if not os.path.exists(source_file):
                raise Exception(f"Source file not found: {source_file}")
            
            # Create OnToology structure in working directory
            target_dir = os.path.join(work_dir, 'OnToology', os.path.dirname(file_path))
            os.makedirs(target_dir, exist_ok=True)
            
            # Copy the ontology file
            target_file = os.path.join(work_dir, file_path)
            target_file_dir = os.path.dirname(target_file)
            if target_file_dir:
                os.makedirs(target_file_dir, exist_ok=True)
            shutil.copy2(source_file, target_file)
            
            dolog(f"Copied {source_file} to {target_file}")
            
            # Update task
            otask.description = 'File copied to working directory'
            otask.save()
            
            # Create default configuration if it doesn't exist
            config_dir = os.path.join(work_dir, 'OnToology', file_path)
            config_file = os.path.join(config_dir, 'OnToology.cfg')
            
            if not os.path.exists(config_file):
                os.makedirs(config_dir, exist_ok=True)
                default_config = get_conf(True, True, True)  # Enable all tools by default
                with open(config_file, 'w') as f:
                    f.write(default_config)
                dolog(f"Created default configuration at {config_file}")
            
            # Update ontology status
            repo.update_ontology_status(ontology=file_path, status='pending')
            
            # Update task
            otask.description = 'Running ontology tools'
            otask.save()
            
            # Run the tools
            try:
                Integrator.tools_execution(
                    changed_files=[file_path],
                    base_dir=work_dir,
                    branch='main',
                    target_repo=virtual_repo_url,
                    g_local=None,  # No GitHub integration for directory processing
                    change_status=change_status,
                    repo=repo,
                    orun=orun,
                    m_logger=logger,
                    logfile=log_file_dir
                )
                
                dolog("Tools execution completed successfully")
                
                # Copy results back to original directory
                ontoology_results = os.path.join(work_dir, 'OnToology', file_path)
                target_results = os.path.join(directory_watch.path, 'OnToology', file_path)
                
                if os.path.exists(ontoology_results):
                    # Ensure target directory exists
                    os.makedirs(os.path.dirname(target_results), exist_ok=True)
                    
                    # Copy results back
                    if os.path.exists(target_results):
                        shutil.rmtree(target_results)
                    shutil.copytree(ontoology_results, target_results)
                    
                    dolog(f"Copied results from {ontoology_results} to {target_results}")
                
                # Update task success
                otask.description = 'Processing completed successfully'
                otask.success = True
                otask.finished = True
                otask.save()
                
                # Update repo state
                repo.state = 'Ready'
                repo.notes = f'Last processed: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}'
                repo.progress = 100
                repo.save()
                
                # Update directory watch last scan time
                directory_watch.last_scan = timezone.now()
                directory_watch.save()
                
                dolog("Directory magic completed successfully")
                
            except Exception as e:
                dolog(f"Error in tools execution: {str(e)}")
                otask.description = f'Error in tools execution: {str(e)}'
                otask.success = False
                otask.finished = True
                otask.save()
                
                repo.state = 'Ready'
                repo.notes = f'Error: {str(e)}'
                repo.save()
                
                if raise_exp:
                    raise
                
        finally:
            # Clean up working directory
            try:
                if os.path.exists(work_dir):
                    shutil.rmtree(work_dir)
                    dolog(f"Cleaned up working directory: {work_dir}")
            except Exception as e:
                dolog(f"Error cleaning up working directory: {str(e)}")
        
    except Exception as e:
        dolog(f"Error in directory_magic: {str(e)}")
        traceback.print_exc()
        
        if 'otask' in locals():
            otask.description = f'Error: {str(e)}'
            otask.success = False
            otask.finished = True
            otask.save()
        
        if 'repo' in locals():
            repo.state = 'Ready'
            repo.notes = f'Error: {str(e)}'
            repo.save()
        
        if raise_exp:
            raise Exception(str(e))

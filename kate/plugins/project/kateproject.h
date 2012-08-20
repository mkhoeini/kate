/*  This file is part of the Kate project.
 *
 *  Copyright (C) 2010 Christoph Cullmann <cullmann@kde.org>
 *
 *  This library is free software; you can redistribute it and/or
 *  modify it under the terms of the GNU Library General Public
 *  License as published by the Free Software Foundation; either
 *  version 2 of the License, or (at your option) any later version.
 *
 *  This library is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 *  Library General Public License for more details.
 *
 *  You should have received a copy of the GNU Library General Public License
 *  along with this library; see the file COPYING.LIB.  If not, write to
 *  the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
 *  Boston, MA 02110-1301, USA.
 */

#ifndef KATE_PROJECT_H
#define KATE_PROJECT_H

#include <QThread>
#include <QMap>
#include <QSharedPointer>

#include "kateprojectindex.h"

/**
 * Shared pointer data types.
 * Used to pass pointers over queued connected slots
 */
typedef QSharedPointer<QStandardItem> KateProjectSharedQStandardItem;
Q_DECLARE_METATYPE(KateProjectSharedQStandardItem)

typedef QSharedPointer<QMap<QString, QStandardItem *> > KateProjectSharedQMapStringItem;
Q_DECLARE_METATYPE(KateProjectSharedQMapStringItem)

typedef QSharedPointer<KateProjectIndex> KateProjectSharedProjectIndex;
Q_DECLARE_METATYPE(KateProjectSharedProjectIndex)

/**
 * Class representing a project.
 * Holds project properties like name, groups, contained files, ...
 */
class KateProject : public QObject
{
  Q_OBJECT

  public:
    /**
     * construct empty project
     */
    KateProject ();
    
    /**
     * deconstruct project
     */
    ~KateProject ();

    /**
     * Load a project.
     * Only works once, afterwards use reload().
     * @param fileName name of project file
     * @return success
     */
    bool load (const QString &fileName);

    /**
     * Try to reload a project.
     * If the reload fails, e.g. because the file is not readable or corrupt, nothing will happen!
     * @param force will enforce the worker to update files list and co even if the content of the file was not changed!
     * @return success
     */
    bool reload (bool force = false);

    /**
     * Accessor to file name.
     * @return file name
     */
    const QString &fileName () const
    {
      return m_fileName;
    }

    /**
     * Accessor to project map containing the whole project info.
     * @return project info
     */
    const QVariantMap &projectMap () const
    {
      return m_projectMap;
    }

    /**
     * Accessor to project name.
     * @return project name
     */
    QString name () const
    {
      return m_projectMap["name"].toString ();
    }

    /**
     * Accessor for the model.
     * @return model of this project
     */
    QStandardItemModel *model ()
    {
      return &m_model;
    }

    /**
     * Flat list of all files in the project
     */
    QStringList files ()
    {
      return m_file2Item->keys ();
    }

    /**
     * get item for file
     * @param file file to get item for
     * @return item for given file or 0
     */
    QStandardItem *itemForFile (const QString &file)
    {
      return m_file2Item->value (file);
    }

    /**
     * Fill in completion matches for given view/range.
     * @param model model to fill with completion matches
     * @param view view we complete for
     * @param range range we complete for
     */
    void completionMatches (QStandardItemModel &model, KTextEditor::View *view, const KTextEditor::Range &range);
    
  private Q_SLOTS:
    /**
     * Used for worker to send back the results of project loading
     * @param topLevel new toplevel element for model
     * @param file2Item new file => item mapping
     */
    void loadProjectDone (KateProjectSharedQStandardItem topLevel, KateProjectSharedQMapStringItem file2Item);
    
    /**
     * Used for worker to send back the results of index loading
     * @param projectIndex new project index
     */
    void loadIndexDone (KateProjectSharedProjectIndex projectIndex);

  signals:
    /**
     * Emited on project map changes.
     * This includes the name!
     */
    void projectMapChanged ();

    /**
     * Emited on model changes.
     * This includes the files list, itemForFile mapping!
     */
    void modelChanged ();

  private:
    /**
     * our internal thread to load stuff and do things in background
     */
    QThread m_thread;

    /**
     * the worker inside the background thread
     * if this is NULL, we are in our deconstruction state and should
     * ignore the feedback of our already stopped thread that
     * may still come in because of queued connects
     * only DELETE all stuff we need to cleanup in the slots
     */
    QObject *m_worker;

    /**
     * project file name
     */
    QString m_fileName;

    /**
     * project name
     */
    QString m_name;

    /**
     * variant map representing the project
     */
    QVariantMap m_projectMap;

    /**
     * standard item model with content of this project
     */
    QStandardItemModel m_model;

    /**
     * mapping files => items
     */
    KateProjectSharedQMapStringItem m_file2Item;
    
    /**
     * project index, if any
     */
    KateProjectSharedProjectIndex m_projectIndex;
};

#endif

// kate: space-indent on; indent-width 2; replace-tabs on;
